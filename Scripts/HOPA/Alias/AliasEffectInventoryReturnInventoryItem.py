from Foundation.DefaultManager import DefaultManager
from Foundation.SceneManager import SceneManager
from Foundation.Task.TaskAlias import TaskAlias


class AliasEffectInventoryReturnInventoryItem(TaskAlias):
    def _onParams(self, params):
        super(AliasEffectInventoryReturnInventoryItem, self)._onParams(params)
        self.Inventory = params.get("Inventory")
        self.InventoryItem = params.get("InventoryItem")
        self.SlotID = params.get("SlotID", None)
        self.item = None

        default_easing = DefaultManager.getDefault("PickEffectTween", "easyLinear")
        self.easing = params.get("Easing", default_easing)
        pass

    def _onInitialize(self):
        super(AliasEffectInventoryReturnInventoryItem, self)._onInitialize()
        pass

    def scope_Generate(self, source):
        CurrentSlotIndex = self.Inventory.getParam("CurrentSlotIndex")
        InventoryItems = self.Inventory.getParam("InventoryItems")

        InventoryItemIndex = InventoryItems.index(self.InventoryItem)

        if self.SlotID is None:
            self.SlotID = InventoryItemIndex - CurrentSlotIndex
            pass

        InventoryEntity = self.Inventory.getEntity()
        InventoryNode = self.Inventory.getEntityNode()
        slots = InventoryEntity.getSlots()

        if self.SlotID >= len(slots):
            self.log("%s slot id %d invalid index for slots [%s]" % (self.name, self.SlotID, slots))
            return
            pass

        slot = slots[self.SlotID]

        point = slot.getPoint()

        Camera = Mengine.getRenderCamera2D()
        P2 = Mengine.getCameraPosition(Camera, point)

        InventoryItemEntityNode = self.InventoryItem.getEntityNode()
        InventoryItemEntity = self.InventoryItem.getEntity()

        P0 = Mengine.getCameraPosition(Camera, InventoryItemEntityNode)

        P1 = (P2.x, P0.y)

        node = Mengine.createNode("Interender")
        node2 = Mengine.createNode("Interender")

        scene = SceneManager.getCurrentScene()
        if Mengine.hasTouchpad() is True:
            layer = scene.getMainLayer()
        else:
            layer = scene.getSlot("InventoryItemEffect")
        layer.addChild(node)
        InventoryNode.addChild(node2)
        node2.setWorldPosition(P2)

        node.setLocalPosition(P0)

        node.addChild(InventoryItemEntityNode)
        InventoryItemEntityNode.setLocalPosition((0.0, 0.0, 0.0))

        scaleTo = DefaultManager.getDefaultFloat("InventoryItemScale", 1.0)

        length = Mengine.length_v2_v2(P0, P2)

        SpeedEffectInventoryReturnInventoryItem = DefaultManager.getDefaultFloat("SpeedEffectInventoryReturnInventoryItem", 1000)
        SpeedEffectInventoryReturnInventoryItem *= 0.001  # speed fix
        time = length / SpeedEffectInventoryReturnInventoryItem
        # time *= 1000  # speed fix

        if InventoryItemEntity.effect is not None:
            effect = InventoryItemEntity.effect
        else:
            effect = self.Inventory.tryGenerateObjectUnique("Effect", "Movie2_ItemTips")

        source.addNotify(Notificator.onInventoryRise)
        if effect is not None:
            effectEntityNode = effect.getEntityNode()

            itemSprite = InventoryItemEntity.getSprite()
            itemSpriteSize = itemSprite.getLocalImageCenter()

            effectEntityNode.setLocalPosition((itemSpriteSize.x, itemSpriteSize.y))

            node.addChildFront(effectEntityNode)
            source.addTask("TaskEnable", Object=effect, Value=True)
            source.addTask("TaskMovie2Play", Movie2=effect, Wait=False)
            pass
        with source.addParallelTask(2) as (tc0, tc1):
            # tc0.addTask("TaskNodeBezier2To", Node=node, Point1=P1, To=P2, Speed=SpeedEffectInventoryReturnInventoryItem)
            tc0.addTask("TaskNodeBezier2WorldFollow", Follow=node2, Node=node,
                        Speed=SpeedEffectInventoryReturnInventoryItem, Easing=self.easing)

            tc1.addTask("TaskNodeScaleTo", Node=node, To=(scaleTo, scaleTo, 1.0), Time=time, Easing=self.easing)
            pass
        source.addTask("TaskNodeEnable", Node=InventoryItemEntityNode, Value=False)
        source.addTask("TaskNodeRemoveFromParent", Node=InventoryItemEntityNode)

        with source.addFork() as source_fork:
            if effect is not None:
                source_fork.addTask("TaskMovie2Interrupt", Movie2=effect)
                source_fork.addTask("TaskObjectDestroy", Object=effect)
                effect = None
            source_fork.addTask("TaskNodeDestroy", Node=node)

            pass

    def _onGenerate(self, source):
        source.addScope(self.scope_Generate)

        return False
