from Foundation.DefaultManager import DefaultManager
from Foundation.GroupManager import GroupManager
from Foundation.Notificator import Notificator
from Foundation.Object.ObjectPoint import ObjectPoint
from Foundation.SceneManager import SceneManager
from Foundation.Task.TaskAlias import TaskAlias
from HOPA.ItemManager import ItemManager

class TaskEffectInventoryAddInventoryItem(TaskAlias):
    def __init__(self):
        super(TaskEffectInventoryAddInventoryItem, self).__init__()

        self.PickEffectNode = None
        self.nodeFollow = None
        self.nodeMove = None
        self.slot = None

        self.ItemName = None
        self.InventoryItem = None
        self.Inventory = None
        self.FromPoint = None
        self.easing = None

    def _onParams(self, params):
        super(TaskEffectInventoryAddInventoryItem, self)._onParams(params)

        self.ItemName = params.get("ItemName", None)
        self.InventoryItem = params.get("InventoryItem", None)
        self.Inventory = params.get("Inventory")
        self.FromPoint = params.get("FromPoint", None)

        default_easing = DefaultManager.getDefault("PickEffectTween", "easyLinear")
        self.easing = params.get("Easing", default_easing)

    def _onGenerate(self, source):
        """Choose method depended on Params, Validate
        """

        if not self.Inventory.isActive():
            msg = 'TaskEffectInventoryAddInventoryItem Inventory is not active'
            Trace.log("Task", 3, msg)
            return

        if SceneManager.getCurrentSceneName() is None:
            msg = 'TaskEffectInventoryAddInventoryItem Scene is None'
            Trace.log("Task", 3, msg)
            return

        if self.InventoryItem is not None:  # CHECK CASE WITH ObjectInventoryItem REFERENCE AS PARAM \\\

            if not self.InventoryItem.isActive():
                msg = 'TaskEffectInventoryAddInventoryItem InventoryItem "%s" is not active' % self.InventoryItem.name
                Trace.log("Task", 3, msg)
                return

            self.__ObjectMovie2ItemEffect(source)  # VALIDATED, RUN MAIN ACTION ///

        elif self.ItemName is not None:  # CHECK CASE WITH ItemName AS PARAM \\\

            Item = ItemManager.getItemObject(self.ItemName)

            if Item is None:
                msg = 'TaskEffectInventoryAddInventoryItem Item "%s" not found in ItemManager' % self.ItemName
                Trace.log("Task", 3, msg)
                return

            InventoryItem = ItemManager.getItemInventoryItem(self.ItemName)

            if InventoryItem is None:
                msg = 'TaskEffectInventoryAddInventoryItem Item "%s" has not InvetoryItem' % self.ItemName
                Trace.log("Task", 3, msg)
                return

            if not InventoryItem.isActive():
                msg = 'TaskEffectInventoryAddInventoryItem InventoryItem "%s" is not active' % InventoryItem.name
                Trace.log("Task", 3, msg)
                return

            ItemType = Item.getType()

            if SceneManager.getCurrentScene() is None:  # LEGACY UNKNOWN FIX
                if ItemType == "ObjectMovie2Item":
                    Item.setEnable(False)
                return

            # Choose method depended from Item instance class:

            if ItemType == "ObjectItem":
                self.__ObjectItemEffect(source)  # VALIDATED, RUN MAIN ACTION ///

            elif ItemType == "ObjectMovie2Item":
                self.__ObjectMovie2ItemEffect(source)  # VALIDATED, RUN MAIN ACTION ///

            else:
                msg = 'TaskEffectInventoryAddInventoryItem Item of Type "%s" not supported' % ItemType
                Trace.log("Task", 3, msg)

        else:
            msg = 'TaskEffectInventoryAddInventoryItem ItemName and InventoryItem can not be both None'
            Trace.log("Task", 3, msg)

    def __ObjectMovie2ItemEffect(self, source):
        """ Main Task Action method for Object Type: Movie2Item
        effect of Bezier_move Movie2Item to inventory
        """

        if self.ItemName is None:
            self.ItemName = self.InventoryItem.name

        PickEffectMovie = None
        InventoryItemEntityNode = None
        Offset = Mengine.vec2f(0.0, 0.0)

        P2 = self.__GetEndPosition()

        if P2 is None:
            source.addDummy()
            return

        self.__CreateNodes()
        self.__AttachNodes()

        if self.InventoryItem is None:  # CASE WITH ItemName AS PARAM
            MovieItem = ItemManager.getItemObject(self.ItemName)

            if not MovieItem.isActive():
                MovieItem.onActivate()

            if self.FromPoint is None:
                PositionFrom = MovieItem.entity.node.getLocalPosition()
            else:
                PositionFrom = self.FromPoint  # Todo: fix this. probably don't need, code can never reach here anyway

            PickEffectMovie = MovieItem.entity.getPickEffectMovie(self.PickEffectNode)

            if PickEffectMovie.hasSlot('center') is True:
                Offset = PickEffectMovie.getMovieSlot('center').getWorldPosition()
            elif PickEffectMovie.hasSocket('socket') is True:
                Offset = PickEffectMovie.getSocket('socket').getWorldPolygonCenter()

            scaleTo = self.calcItemScaleTo(PickEffectMovie)

            PickEffectMoveEntityNode = PickEffectMovie.entity.node
            PickEffectMoveEntityNode.setWorldPosition(Offset)
            PickEffectMoveEntityNode.setOrigin(Offset)
            nodeScale = PickEffectMoveEntityNode

            self.nodeMove.addChild(nodeScale)

            self.nodeFollow.setLocalPosition(P2 - Offset + PositionFrom)

            source.addDisable(MovieItem)

        else:  # CASE WITH ObjectInventoryItem REFERENCE AS PARAM
            if self.FromPoint is None:
                PositionFrom = self.calcMovieItemPositionFrom(self.InventoryItem)

            elif isinstance(self.FromPoint, ObjectPoint):
                PositionFrom = self.FromPoint.entity.getLocalPosition()

            elif isinstance(self.FromPoint, tuple):
                PositionFrom = Mengine.vec3f(self.FromPoint[0], self.FromPoint[1], 0.0)

            else:
                msg = "Invalid self.FromPoint type '{}', should be None, ObjectPoint or tuple(float_x, float_y)"
                msg = msg.format(type(self.FromPoint))
                self.log(msg)

                PositionFrom = Mengine.vec3f(0.0, 0.0, 0.0)

            scaleTo = 1.0

            InventoryItemEntityNode = self.InventoryItem.entity.node
            InventoryItemEntityNode.setLocalPosition(Offset)

            nodeScale = self.PickEffectNode
            nodeScale.setWorldPosition(PositionFrom)
            nodeScale.addChild(InventoryItemEntityNode)

            self.nodeMove.addChild(nodeScale)

            itemSpriteSize = self.InventoryItem.entity.getSpriteCenter()
            Offset = itemSpriteSize.x, itemSpriteSize.y

            self.nodeFollow.setWorldPosition(P2 - PositionFrom - Offset)

            source.addEnable(self.InventoryItem)

        P0 = PositionFrom + Offset
        Speed, Time = self.calcSpeedAndTimeForItemScale(P0, P2)

        # print "! P0={} FROM={} P2={} ||| time={} speed={} offset={}".format(P0, PositionFrom, P2, Time, Speed, Offset)

        # -----------------------------------------------------------
        # task chain execution source definition:
        # -----------------------------------------------------------

        source.addNotify(Notificator.onInventoryRise)
        source.addFunction(self.slot.setBlock, True)

        effect = self.Inventory.tryGenerateObjectUnique("Effect", "Movie2_ItemTips")
        if effect is not None:
            effectEntityNode = effect.entity.node
            self.nodeMove.addChildFront(effectEntityNode)

            if self.InventoryItem is None:
                effect_position = Offset
            else:
                effect_position = PositionFrom + Offset

            effectEntityNode.setLocalPosition(effect_position)

            source.addTask("TaskEnable", Object=effect, Value=True)
            source.addTask("TaskMovie2Play", Movie2=effect, Wait=False)

        with source.addParallelTask(2) as (parallel_0, parallel_1):
            parallel_0.addTask("TaskNodeBezier2Follow", Follow=self.nodeFollow, Node=self.nodeMove, Time=Time, Easing=self.easing)
            parallel_1.addTask("TaskNodeScaleTo", Node=nodeScale, To=(scaleTo, scaleTo, 1.0), Time=Time, Easing=self.easing)

        source.addFunction(self.slot.setBlock, False)

        if PickEffectMovie is not None:
            source.addFunction(PickEffectMovie.onDestroy)

        if InventoryItemEntityNode is not None:
            slot = self.Inventory.entity.findSlot(self.InventoryItem)

            source.addTask("TaskNodeRemoveFromParent", Node=InventoryItemEntityNode)
            source.addFunction(slot.setItem, self.InventoryItem)

        with source.addFork() as source_fork:
            if effect is not None:
                source_fork.addTask("TaskMovie2Interrupt", Movie2=effect)
                source_fork.addTask("TaskObjectDestroy", Object=effect)

            source_fork.addTask("TaskNodeDestroy", Node=self.PickEffectNode)
            source_fork.addTask("TaskNodeDestroy", Node=self.nodeFollow)
            source_fork.addTask("TaskNodeDestroy", Node=self.nodeMove)

    def __ObjectItemEffect(self, source):
        """ Main Task Action method for Object Type: Item
        effect of Bezier_move Item to inventory
        """

        Camera = Mengine.getRenderCamera2D()
        Item = ItemManager.getItemObject(self.ItemName)
        ItemEntity = Item.entity
        P0 = ItemEntity.getCameraPosition(Camera)
        P2 = self.__GetEndPosition()
        Point1 = P2.x, P0.y

        sprite = ItemEntity.generatePure()
        layer = self._getAttachLayer()
        layer.addChild(sprite)
        sprite.setLocalPosition(P0)
        size = sprite.getSurfaceSize()
        scaleTo = self.calcItemScaleTo(size)

        Speed, Time = self.calcSpeedAndTimeForItemScale(Point1, P2)

        # print "!!! P0={} P1={} P2={} ||| time={} speed={}".format(P0, Point1, P2, Time, Speed)

        with source.addParallelTask(2) as (parallel_0, parallel_1):
            parallel_0.addNotify(Notificator.onSoundEffectOnObject, Item, "MoveItemToInventory")
            parallel_0.addTask("TaskNodeBezier2To", Node=sprite, Point1=Point1, To=P2, Speed=Speed)
            parallel_1.addTask("TaskNodeScaleTo", Node=sprite, To=(scaleTo, scaleTo, 1.0), Time=Time)

        source.addTask("TaskNodeRemoveFromParent", Node=sprite)
        source.addTask("TaskNodeDestroy", Node=sprite)

    @staticmethod
    def calcSpeedAndTimeForItemScale(pos_1, pos_2):
        """Helper
        """

        speed = DefaultManager.getDefaultFloat("SpeedEffectInventoryAddInventoryItem", 1000) * 0.001  # speed fix
        time = Mengine.length_v2_v2(pos_1, pos_2) / speed

        return speed, time

    @staticmethod
    def calcItemScaleTo(PickEffectMovie):
        """Helper
        """

        if PickEffectMovie.hasSocket('socket') is True:
            socket = PickEffectMovie.getSocket('socket')
            node_box = Mengine.getHotSpotPolygonBoundingBox(socket)

            InventorySlotSize = DefaultManager.getDefaultFloat("InventorySlotSize", 70)
            node_size = Mengine.vec2f(node_box.maximum.x - node_box.minimum.x, node_box.maximum.y - node_box.minimum.y)

            scaleToX = InventorySlotSize / node_size.x
            scaleToY = InventorySlotSize / node_size.y

            scaleTo = min(scaleToX, scaleToY)

        else:
            scaleTo = 1.0

        return scaleTo

    @staticmethod
    def calcMovieItemPositionFrom(MovieItem):
        """Helper
        """

        ItemSpriteCenter = MovieItem.entity.getSpriteCenter()

        Camera = Mengine.getRenderCamera2D()

        GroupPopUp = GroupManager.getGroup("ItemPopUp")
        Demon_ItemPopUp = GroupPopUp.getObject("Demon_ItemPopUp")
        Point_Item = Demon_ItemPopUp.getObject("Point_Item")

        PointItemCameraPosition = Point_Item.entity.getCameraPosition(Camera)

        return Mengine.vec2f(PointItemCameraPosition.x - ItemSpriteCenter.x, PointItemCameraPosition.y - ItemSpriteCenter.y)

    def __CreateNodes(self):
        """Helper
        """

        self.PickEffectNode = Mengine.createNode("Interender")
        self.nodeFollow = Mengine.createNode("Interender")
        self.nodeMove = Mengine.createNode("Interender")

        self.PickEffectNode.setName("PickEffectNode_" + self.ItemName)
        self.nodeFollow.setName("nodeFollow_" + self.ItemName)
        self.nodeMove.setName("nodeMove_" + self.ItemName)

    def __AttachNodes(self):
        """ Helper """

        AttachLayer = self._getAttachLayer()
        InventoryNode = self.Inventory.entity.node

        AttachLayer.addChild(self.PickEffectNode)
        AttachLayer.addChild(self.nodeMove)
        InventoryNode.addChild(self.nodeFollow)

    def __GetEndPosition(self):
        """ Helper """

        if self.InventoryItem is None:
            InventoryItem = ItemManager.getItemInventoryItem(self.ItemName)
        else:
            InventoryItem = self.InventoryItem

        slot = self.Inventory.entity.findSlot(InventoryItem)

        if slot is None:
            if _DEVELOPMENT is True:
                Trace.log("Task", 0, "TaskEffectInventoryAddInventoryItem: not found slot for {} in {}".format(InventoryItem.getName(), self.Inventory.getName()))
            return

        self.slot = slot

        InventorySlotSize = DefaultManager.getDefaultFloat("InventorySlotSize", 70)

        P2 = self.slot.getPoint().getWorldPosition()

        P2.x = P2.x + InventorySlotSize / 2
        P2.y = P2.y + InventorySlotSize / 2

        return P2

    def _getAttachLayer(self):
        scene = SceneManager.getCurrentScene()
        layer = scene.getSlot("InventoryItemEffect")
        return layer