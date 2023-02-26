from Foundation.DefaultManager import DefaultManager
from Foundation.SceneManager import SceneManager
from Foundation.Task.TaskAlias import TaskAlias
from HOPA.ItemManager import ItemManager

class PolicyEffectInventoryAddInventoryItemParticles(TaskAlias):
    def _onParams(self, params):
        super(PolicyEffectInventoryAddInventoryItemParticles, self)._onParams(params)
        self.ItemName = params.get("ItemName")
        self.Inventory = params.get("Inventory")
        self.hasInventoryItem = params.get("hasInventoryItem")
        pass

    def _onGenerate(self, source):
        if self.Inventory.isActive() is False:
            return
            pass

        effect = self.Inventory.tryGenerateObjectUnique("Effect", "Movie2_ItemTips")

        InventoryEntity = self.Inventory.getEntity()
        InventoryItem = ItemManager.getItemInventoryItem(self.ItemName)

        slot = InventoryEntity.findSlot(InventoryItem)

        point = slot.getPoint()

        Camera = Mengine.getRenderCamera2D()
        P2 = Mengine.getCameraPosition(Camera, point)

        Item = ItemManager.getItemObject(self.ItemName)
        ItemEntity = Item.getEntity()
        sprite = ItemEntity.generatePure()
        InventoryItemEntityNode = InventoryItem.getEntityNode()
        if self.hasInventoryItem is False:
            InventoryItemEntityNode.disable()
            pass
        size = sprite.getSurfaceSize()

        P0 = ItemEntity.getCameraPosition(Camera)

        P1 = (P2.x, P0.y)

        scene = SceneManager.getCurrentScene()
        layer_InventoryItemEffect = scene.getSlot("InventoryItemEffect")
        layer_InventoryItemEffect.addChild(sprite)

        sprite.setLocalPosition(P0)

        InventorySlotSize = DefaultManager.getDefaultFloat("InventorySlotSize", 70)

        scaleToX = InventorySlotSize / size.x
        scaleToY = InventorySlotSize / size.y

        scaleTo = min(scaleToX, scaleToY)

        length = Mengine.length_v2_v2(P1, P2)

        SpeedEffectInventoryAddInventoryItem = DefaultManager.getDefaultFloat("SpeedEffectInventoryAddInventoryItem", 1000.0)
        SpeedEffectInventoryAddInventoryItem *= 0.001  # speed fix
        time = length / SpeedEffectInventoryAddInventoryItem
        # time *= 1000 # speed fix

        if effect is not None:
            effectEntityNode = effect.getEntityNode()

            itemSpriteSize = sprite.getLocalImageCenter()

            sprite.addChildFront(effectEntityNode)

            effectEntityNode.setLocalPosition(itemSpriteSize)

            source.addTask("TaskEnable", Object=effect, Value=True)
            source.addTask("TaskMovie2Play", Movie2=effect, Wait=False)
            pass

        with source.addParallelTask(2) as (tcp0, tcp1):
            tcp0.addTask("TaskNodeBezier2To", Node=sprite, Point1=P1, To=P2, Speed=SpeedEffectInventoryAddInventoryItem)
            tcp1.addTask("TaskNodeScaleTo", Node=sprite, To=(scaleTo, scaleTo, 1.0), Time=time)
            pass

        if effect is not None:
            effectEntityNode = effect.getEntityNode()

            source.addTask("TaskMovie2Stop", Movie2=effect)

            if effect is not None:
                with source.addFork() as source_fork:
                    source_fork.addTask("TaskMovie2Interrupt", Movie2=effect)
                    source_fork.addTask("TaskObjectDestroy", Object=effect)

            source.addTask("TaskNodeRemoveFromParent", Node=effectEntityNode)
            pass

        source.addTask("TaskNodeEnable", Node=sprite, Value=False)
        source.addTask("TaskNodeRemoveFromParent", Node=sprite)

        source.addTask("TaskNodeDestroy", Node=sprite)

        if self.hasInventoryItem is False:
            source.addTask("TaskNodeEnable", Node=InventoryItemEntityNode, Value=True)
            pass
        pass
    pass