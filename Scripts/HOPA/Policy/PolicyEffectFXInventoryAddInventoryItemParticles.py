from Foundation.DefaultManager import DefaultManager
from Foundation.SceneManager import SceneManager
from Foundation.Task.TaskAlias import TaskAlias
from HOPA.ItemManager import ItemManager


class PolicyEffectFXInventoryAddInventoryItemParticles(TaskAlias):
    def _onParams(self, params):
        super(PolicyEffectFXInventoryAddInventoryItemParticles, self)._onParams(params)
        self.ItemName = params.get("ItemName")
        self.Inventory = params.get("Inventory")
        pass

    def _onGenerate(self, source):
        if self.Inventory.isActive() is False:
            return
            pass

        effect = self.Inventory.tryGenerateObjectUnique("Effect", "Movie2_ItemTips")

        InventoryEntity = self.Inventory.getEntity()
        InventoryItem = ItemManager.getItemInventoryItem(self.ItemName)

        CountRight = self.Inventory.getScrollCountRight(InventoryItem)
        CountLeft = self.Inventory.getScrollCountLeft(InventoryItem)
        if CountRight >= 1:
            slot = InventoryEntity.getSlot(0)
            pass
        elif CountLeft >= 1:
            lastIndex = DefaultManager.getDefaultInt("InventorySlotCount", 7) - 1
            slot = InventoryEntity.getSlot(lastIndex)
            pass
        else:
            slot = InventoryEntity.findSlot(InventoryItem)
            pass

        InvItemFoundItems = InventoryItem.getFoundItems()
        # print "InvItemFoundItems", InvItemFoundItems
        if len(InvItemFoundItems) <= 1:
            InventoryItem.setEnable(False)
            slot.hotspot.disable()
            pass

        point = slot.getPoint()

        Camera = Mengine.getRenderCamera2D()
        P2 = Mengine.getCameraPosition(Camera, point)

        Item = ItemManager.getItemObject(self.ItemName)
        ItemEntity = Item.getEntity()
        sprite = ItemEntity.getSprite()
        pure = ItemEntity.generatePure()
        pure.disable()

        size = sprite.getSurfaceSize()

        P0 = ItemEntity.getCameraPosition(Camera)

        P1 = (P2.x, P0.y)

        scene = SceneManager.getCurrentScene()
        layer_InventoryItemEffect = scene.getSlot("InventoryItemEffect")
        layer_InventoryItemEffect.addChild(pure)

        pure.setLocalPosition(P0)

        InventorySlotSize = DefaultManager.getDefaultFloat("InventorySlotSize", 70)

        scaleToX = InventorySlotSize / size.x
        scaleToY = InventorySlotSize / size.y

        scaleTo = min(scaleToX, scaleToY)

        length = Mengine.length_v2_v2(P1, P2)

        SpeedEffectInventoryAddInventoryItem = DefaultManager.getDefaultFloat("SpeedEffectInventoryAddInventoryItem", 1000.0)
        SpeedEffectInventoryAddInventoryItem *= 0.001  # speed fix
        time = length / SpeedEffectInventoryAddInventoryItem
        # time *= 1000  #speed fix

        if effect is not None:
            effectEntity = effect.getEntity()
            effectEntityNode = effect.getEntityNode()

            itemSpriteSize = pure.getLocalImageCenter()

            pure.addChildFront(effectEntityNode)

            effectEntityNode.setLocalPosition((itemSpriteSize.x, itemSpriteSize.y))

            source.addTask("TaskEnable", Object=effect, Value=True)
            source.addTask("TaskMovie2Play", Movie2=effect, Wait=False)
            pass

        source.addTask("TaskNodeEnable", Node=pure, Value=True)

        with source.addParallelTask(2) as (tcp0, tcp1):
            tcp0.addTask("TaskNodeBezier2To", Node=pure, Point1=P1, To=P2, Speed=SpeedEffectInventoryAddInventoryItem)
            tcp1.addTask("TaskNodeScaleTo", Node=pure, To=(scaleTo, scaleTo, 1.0), Time=time)
            pass

        if len(InvItemFoundItems) == 1:
            source.addTask("TaskEnable", Object=InventoryItem, Value=True)
            source.addTask("TaskNodeEnable", Node=slot.hotspot, Value=True)
            pass

        if effect is not None:
            effectEntity = effect.getEntity()
            effectEntityNode = effect.getEntityNode()

            source.addTask("TaskMovie2Stop", Movie2=effect)
            if effect is not None:
                with source.addFork() as source_fork:
                    source_fork.addTask("TaskMovie2Interrupt", Movie2=effect)
                    source_fork.addTask("TaskObjectDestroy", Object=effect)
            source.addTask("TaskNodeRemoveFromParent", Node=effectEntityNode)
            pass

        source.addTask("TaskNodeRemoveFromParent", Node=pure)
        source.addTask("TaskNodeDestroy", Node=pure)

        pass

    pass
