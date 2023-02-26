from Foundation.DefaultManager import DefaultManager
from Foundation.SceneManager import SceneManager
from Foundation.Task.TaskAlias import TaskAlias
from HOPA.HOGManager import HOGManager

class AliasHOGRollingItemFoundEffect(TaskAlias):
    def _onParams(self, params):
        super(AliasHOGRollingItemFoundEffect, self)._onParams(params)
        self.HOGItemName = params.get("HOGItemName")
        self.HOG = params.get("HOG")
        self.EnigmaName = params.get("EnigmaName")
        pass

    def _onGenerate(self, source):
        HOGInventory = HOGManager.getInventory(self.EnigmaName)

        if HOGInventory.isActive() is False:
            return
            pass

        effect = HOGInventory.tryGenerateObjectUnique("Effect", "Movie2_ItemTips")

        hogItem = HOGManager.getHOGItem(self.EnigmaName, self.HOGItemName)
        self.ItemName = hogItem.objectName

        InventoryEntity = HOGInventory.getEntity()
        slot = InventoryEntity.getSlotByName(self.HOGItemName)

        if slot is None:
            self.invalidTask("not found slot %s" % (self.HOGItemName))
            pass

        P2 = slot.getPoint()

        Camera = Mengine.getRenderCamera2D()

        Item = self.Group.getObject(self.ItemName)
        Item.setBlock(False)
        ItemEntity = Item.getEntity()

        node = Mengine.createNode("Interender")

        pure = ItemEntity.generatePure()
        pure.enable()

        # tempPos = ItemEntity.getCameraPosition(Camera)
        # offset = pure.getWorldPosition()
        # offsetPos = (tempPos[0] + offset.x, tempPos[1] + offset.y)

        # P0 = (offsetPos[0] + pureCenter.x, offsetPos[1] + pureCenter.y)
        P0 = ItemEntity.getCameraPosition(Camera)

        P1 = (P2.x, P0[1])

        scene = SceneManager.getCurrentScene()
        if Mengine.hasTouchpad() is True:
            layer = scene.getMainLayer()
        else:
            layer = scene.getSlot("HOGViewport")
        layer.addChild(node)

        node.addChild(pure)
        node.setLocalPosition(P0)

        pureCenter = pure.getLocalImageCenter()
        pure.coordinate(pureCenter)

        length = Mengine.length_v2_v2(P1, P2)

        HOGItemHideEffectSpeed = DefaultManager.getDefaultFloat("HOGItemHideEffectSpeed", 1000)
        HOGItemHideEffectSpeed *= 0.001  # speed fix
        HOGItemIncreaseTime = DefaultManager.getDefaultFloat("HOGItemIncreaseTime", 1)
        HOGItemIncreaseTime *= 1000  # speed fix

        time = length / HOGItemHideEffectSpeed
        # time *= 1000  # speed fix

        source.addTask("TaskNodeScaleTo", Node=pure, To=(1.5, 1.5, 1.0), Time=HOGItemIncreaseTime)

        if effect is not None:
            effectEntityNode = effect.getEntityNode()

            itemSpriteSize = pure.getLocalImageCenter()
            effectEntityNode.setLocalPosition((itemSpriteSize.x, itemSpriteSize.y))

            node.addChildrFront(effectEntityNode)

            source.addTask("TaskEnable", Object=effect, Value=True)
            source.addTask("TaskMovie2Play", Movie2=effect, Wait=False)
            pass

        with source.addParallelTask(2) as (tcp0, tcp1):
            tcp0.addTask("TaskNodeBezier2To", Node=node, Point1=P1, To=P2, Speed=HOGItemHideEffectSpeed)

            tcp1.addTask("TaskNodeScaleTo", Node=node, To=(0.4, 0.4, 1.0), Time=time)
            pass

        source.addTask("TaskNodeEnable", Node=pure, Value=False)

        with source.addFork() as source_fork:
            if effect is not None:
                source_fork.addTask("TaskMovie2Interrupt", Movie2=effect)
                source_fork.addTask("TaskObjectDestroy", Object=effect)
                pass

            source_fork.addTask("TaskNodeDestroy", Node=node)
            pass

        if slot.getCount() != 1:
            return
            pass

        # source.addTask("TaskMoviePlay", Movie = slot.movie, Wait = True)

        def __playMovie(scope):
            # Inventory can be switched during the time item flies. Just to ensure we take movie from right inventory.
            HOGInventory = HOGManager.getInventory(self.EnigmaName)
            InventoryEntity = HOGInventory.getEntity()
            slot = InventoryEntity.getSlotByName(self.HOGItemName)
            if slot and slot.movie:
                scope.addTask("TaskMoviePlay", Movie=slot.movie, Wait=True)
                pass
            pass

        source.addTask("TaskScope", Scope=__playMovie)
        pass

    pass