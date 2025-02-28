from Foundation.DefaultManager import DefaultManager
from Foundation.SceneManager import SceneManager
from Foundation.Task.TaskAlias import TaskAlias
from HOPA.ItemManager import ItemManager


class PolicyEffectInventoryAddInventoryItemParticles2(TaskAlias):
    def _onParams(self, params):
        super(PolicyEffectInventoryAddInventoryItemParticles2, self)._onParams(params)
        self.ItemName = params.get("ItemName")
        self.Inventory = params.get("Inventory")
        self.hasInventoryItem = params.get("hasInventoryItem", None)
        pass

    def _onGenerate(self, source):
        if self.Inventory.isActive() is False:
            return
            pass

        scene = SceneManager.getCurrentScene()

        if scene is None:
            return
            pass

        effect = self.Inventory.tryGenerateObjectUnique("Effect", "Movie2_ItemTips")

        InventoryEntity = self.Inventory.getEntity()
        InventoryItem = ItemManager.getItemInventoryItem(self.ItemName)

        slot = InventoryEntity.findSlot(InventoryItem)

        if slot is None:
            self.log("invalid find slot for inventory item %s:%s" % (self.ItemName, InventoryItem))
            return
            pass

        point = slot.getPoint()

        Item = ItemManager.getItemObject(self.ItemName)
        ItemEntity = Item.getEntity()

        Camera = Mengine.getRenderCamera2D()
        P2 = Mengine.getCameraPosition(Camera, point)

        node = Mengine.createNode("Interender")

        sprite = ItemEntity.generatePure()
        imageSize = sprite.getSurfaceSize()

        P0 = ItemEntity.getCameraPosition(Camera)

        P1 = (P2.x, P0.y)

        layer_InventoryItemEffect = scene.getSlot("InventoryItemEffect")
        layer_InventoryItemEffect.addChild(node)

        spriteCenter = sprite.getLocalImageCenter()
        sprite.coordinate(spriteCenter)

        node.setLocalPosition(P0)

        node.addChild(sprite)

        InventorySlotSize = DefaultManager.getDefaultFloat("InventorySlotSize", 70)

        scaleToX = InventorySlotSize / imageSize.x
        scaleToY = InventorySlotSize / imageSize.y

        scaleTo = min(scaleToX, scaleToY)

        length = Mengine.length_v2_v2(P1, P2)

        SpeedEffectInventoryAddInventoryItem = DefaultManager.getDefaultFloat("SpeedEffectInventoryAddInventoryItem", 1000.0)
        SpeedEffectInventoryAddInventoryItem *= 0.001  # speed fix
        time = length / SpeedEffectInventoryAddInventoryItem
        # time *= 1000  # speed fix

        source.addTask("TaskNodeScaleTo", Node=sprite, To=(1.25, 1.25, 1.0), Time=250.0)
        source.addTask("TaskNodeScaleTo", Node=sprite, To=(1.0, 1.0, 1.0), Time=250.0)

        if effect is not None:
            effectEntityNode = effect.getEntityNode()

            itemSpriteSize = sprite.getLocalImageCenter()
            effectEntityNode.setLocalPosition((itemSpriteSize.x, itemSpriteSize.y))

            node.addChildFront(effectEntityNode)

            source.addEnable(effect)
            source.addTask("TaskMovie2Play", Movie2=effect, Wait=False)
            pass

        with source.addParallelTask(2) as (tcp0, tcp1):
            tcp0.addNotify(Notificator.onSoundEffectOnObject, Item, "MoveItemToInventory")
            tcp0.addTask("TaskNodeBezier2To", Node=node, Point1=P1, To=P2, Speed=SpeedEffectInventoryAddInventoryItem)
            tcp1.addTask("TaskNodeScaleTo", Node=node, To=(scaleTo, scaleTo, 1.0), Time=time)
            pass

        source.addTask("TaskNodeEnable", Node=sprite, Value=False)

        with source.addFork() as source_fork:
            if effect is not None:
                source_fork.addTask("TaskMovie2Interrupt", Movie2=effect)
                source_fork.addTask("TaskObjectDestroy", Object=effect)
                pass

            source_fork.addTask("TaskNodeDestroy", Node=node)
            pass
        pass

    pass
