from Foundation.DefaultManager import DefaultManager
from Foundation.GroupManager import GroupManager
from Foundation.SceneManager import SceneManager
from Foundation.Task.TaskAlias import TaskAlias
from HOPA.ItemManager import ItemManager


class PolicyEffectInventoryAddInventoryItemWithItemPopup(TaskAlias):
    def _onParams(self, params):
        super(PolicyEffectInventoryAddInventoryItemWithItemPopup, self)._onParams(params)

        self.ItemName = params.get("ItemName")
        self.Inventory = params.get("Inventory")
        self.hasInventoryItem = params.get("hasInventoryItem", None)
        pass

    def _onInitialize(self):
        super(PolicyEffectInventoryAddInventoryItemWithItemPopup, self)._onInitialize()

        self.effect = None
        self.sprite = None
        self.node = None

        self.start_pos = None
        self.end_pos = None
        pass

    def _onCheck(self):
        super(PolicyEffectInventoryAddInventoryItemWithItemPopup, self)._onCheck()
        if self.Inventory.isActive() is False:
            return False
            pass

        scene = SceneManager.getCurrentScene()
        if scene is None:
            return False
            pass

        InventoryEntity = self.Inventory.getEntity()
        InventoryItem = ItemManager.getItemInventoryItem(self.ItemName)

        slot = InventoryEntity.findSlot(InventoryItem)

        if slot is None:
            msg = "{ClassName}: invalid find slot for inventory item {Name}:{Object}".format(ClassName=self.__name__, Name=self.ItemName, Object=InventoryItem)
            Trace.log("Policy", 0, msg)
            return False
            pass

        return True
        pass

    def _start_effect_scope(self, source):
        if self.effect is None:
            return

        effectEntityNode = self.effect.getEntityNode()

        itemSpriteSize = self.sprite.getLocalImageCenter()
        effectEntityNode.setLocalPosition((itemSpriteSize.x, itemSpriteSize.y))

        self.node.addChildFront(effectEntityNode)

        source.addEnable(self.effect)
        source.addTask("TaskMovie2Play", Movie2=self.effect, Wait=False)
        pass

    def _setup(self):
        # def service vars
        scene = SceneManager.getCurrentScene()
        layer_InventoryItemEffect = scene.getSlot("InventoryItemEffect")

        Item = ItemManager.getItemObject(self.ItemName)
        ItemEntity = Item.getEntity()
        Camera = Mengine.getRenderCamera2D()

        InventorySlotSize = DefaultManager.getDefaultFloat("InventorySlotSize", 70)

        # calc start pos
        self.start_pos = ItemEntity.getCameraPosition(Camera)

        # setup effect
        self.effect = self.Inventory.tryGenerateObjectUnique("Effect", "Movie2_ItemTips")

        # setup node
        self.node = Mengine.createNode("Interender")
        layer_InventoryItemEffect.addChild(self.node)

        self.node.setLocalPosition(self.start_pos)

        # setup sprite
        self.sprite = ItemEntity.generatePure()

        spriteCenter = self.sprite.getLocalImageCenter()
        self.sprite.coordinate(spriteCenter)

        self.node.addChild(self.sprite)

        # calc end pos
        bb = self.sprite.getBoundingBox()
        sprite_w, sprite_h = bb.maximum.x - bb.minimum.x, bb.maximum.y - bb.minimum.y

        offset_x, offset_y = sprite_w / 2, sprite_h / 2

        Demon = GroupManager.getObject("ItemPopUp", "Demon_ItemPopUp")
        Point = Demon.getObject("Point_Item")

        pos_x, pos_y = Point.getPosition()

        imageSize = self.sprite.getSurfaceSize()

        scaleToX = InventorySlotSize / imageSize.x
        scaleToY = InventorySlotSize / imageSize.y
        scaleTo = min(scaleToX, scaleToY)

        self.end_pos = (pos_x - offset_x * scaleTo, pos_y - offset_y * scaleTo)
        pass

    def _scale_scope(self, source):
        source.addTask("TaskNodeScaleTo", Node=self.sprite, To=(1.25, 1.25, 1.0), Time=250.0)
        source.addTask("TaskNodeScaleTo", Node=self.sprite, To=(1.0, 1.0, 1.0), Time=250.0)
        pass

    def _clean_scope(self, source):
        with source.addFork() as source_fork:
            if self.effect is not None:
                source_fork.addTask("TaskMovie2Interrupt", Movie2=self.effect)
                source_fork.addTask("TaskObjectDestroy", Object=self.effect)
                pass

            source_fork.addTask("TaskNodeDestroy", Node=self.node)
            pass
        pass

    def _move_to_center_scope(self, source):
        # def vars
        Item = ItemManager.getItemObject(self.ItemName)
        imageSize = self.sprite.getSurfaceSize()
        InventorySlotSize = DefaultManager.getDefaultFloat("InventorySlotSize", 70)

        # calc scale to
        scaleToX = InventorySlotSize / imageSize.x
        scaleToY = InventorySlotSize / imageSize.y
        scaleTo = min(scaleToX, scaleToY)

        # calc time
        length = Mengine.length_v2_v2(self.start_pos, self.end_pos)
        SpeedEffectInventoryAddInventoryItem = DefaultManager.getDefaultFloat("SpeedEffectInventoryAddInventoryItem", 1000.0)
        SpeedEffectInventoryAddInventoryItem *= 0.001  # speed fix
        time = length / SpeedEffectInventoryAddInventoryItem

        # task chain
        with source.addParallelTask(2) as (tcp0, tcp1):
            tcp0.addNotify(Notificator.onSoundEffectOnObject, Item, "MoveItemToInventory")
            tcp0.addTask("TaskNodeBezier2To", Node=self.node, Point1=self.start_pos, To=self.end_pos,
                         Speed=SpeedEffectInventoryAddInventoryItem)

            tcp1.addTask("TaskNodeScaleTo", Node=self.node, To=(scaleTo, scaleTo, 1.0), Time=time)
            pass
        pass

    def _get_item_scope(self, source):
        # source.addTask("AliasInventoryGetInventoryItem", ItemName=self.ItemName, Inventory=self.Inventory)
        # def vars
        InventoryItem = ItemManager.getItemInventoryItem(self.ItemName)

        # filter for get item
        def __isItem(inventory, invItem):
            if InventoryItem is not invItem:
                return False

            return True
            pass

        # task chains
        source.addNotify(Notificator.onItemPopUp, self.ItemName)

        source.addDelay(200.0)
        source.addTask("TaskNodeAlphaTo", Node=self.sprite, From=1.0, To=0.0, Time=250.0)
        source.addTask("TaskNodeEnable", Node=self.sprite, Value=False)

        source.addListener(Notificator.onGetItem, Filter=__isItem)
        pass

    def _onGenerate(self, source):
        self._setup()

        source.addScope(self._scale_scope)

        source.addScope(self._start_effect_scope)

        source.addScope(self._move_to_center_scope)

        source.addScope(self._get_item_scope)

        source.addScope(self._clean_scope)
        pass

    pass
