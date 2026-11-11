from Foundation.DefaultManager import DefaultManager
from Foundation.GroupManager import GroupManager
from Foundation.SceneManager import SceneManager
from Foundation.Task.TaskScopeChain import TaskScopeChain


class TaskEffectFittingInventoryGetInventoryItem(TaskScopeChain):
    def _onParams(self, params):
        super(TaskEffectFittingInventoryGetInventoryItem, self)._onParams(params)
        self.FittingInventory = params.get("FittingInventory")
        self.inventoryItem = params.get("InventoryItem")
        self.NodeCopyInventoryItem = None
        self.SlotID = params.get("SlotID", None)
        pass

    def _onScopeRun(self, source):
        inventoryItemEntity = self.inventoryItem.getEntity()
        inventoryItemSprite = inventoryItemEntity.getSprite()
        inventoryItemImageResource = inventoryItemSprite.getResourceImage()
        centerInventoryItemSprite = inventoryItemSprite.getLocalImageCenter()

        self.NodeCopyInventoryItem = Mengine.createSprite("NodeCopyInventoryItem", inventoryItemImageResource)

        self.NodeCopyInventoryItem.setLocalAlpha(0.0)
        self.NodeCopyInventoryItem.enable()

        Camera = Mengine.getRenderCamera2D()
        P2 = inventoryItemEntity.getCameraPosition(Camera)

        scene = SceneManager.getCurrentScene()
        layer_InventoryItemEffect = scene.getSlot("InventoryItemEffect")
        layer_InventoryItemEffect.addChild(self.NodeCopyInventoryItem)

        GroupPopUp = GroupManager.getGroup("ItemPopUp")
        Demon_ItemPopUp = GroupPopUp.getObject("Demon_ItemPopUp")
        Point_Item = Demon_ItemPopUp.getObject("Point_Item")

        P0 = Point_Item.getEntity().getCameraPosition(Camera)
        P1 = (P2.x, P0.y)

        self.NodeCopyInventoryItem.setLocalPosition(P0)
        self.NodeCopyInventoryItem.setOrigin(centerInventoryItemSprite)
        self.NodeCopyInventoryItem.enable()

        TimeEffectFittingInventoryAlphaInventoryItem = DefaultManager.getDefaultFloat("TimeEffectFittingInventoryAlphaInventoryItem", 2.0)
        TimeEffectFittingInventoryAlphaInventoryItem *= 1000  # speed fix
        source.addTask("TaskNodeAlphaTo", Node=self.NodeCopyInventoryItem,
                   Time=TimeEffectFittingInventoryAlphaInventoryItem, To=1.0)

        SpeedEffectFittingInventoryGetItem = DefaultManager.getDefaultFloat("SpeedEffectFittingInventoryGetItem", 2000.0)
        SpeedEffectFittingInventoryGetItem *= 0.001  # speed fix
        source.addTask("TaskNodeBezier2To", Node=self.NodeCopyInventoryItem, Point1=P1, To=P2,
                   Speed=SpeedEffectFittingInventoryGetItem)
        pass

    def _onScopeComplete(self, isSkip):
        self.NodeCopyInventoryItem.disable()
        Mengine.destroyNode(self.NodeCopyInventoryItem)
        self.NodeCopyInventoryItem = None
        pass

    def _onFinally(self):
        super(TaskEffectFittingInventoryGetInventoryItem, self)._onFinally()

        if self.NodeCopyInventoryItem is not None:
            Mengine.destroyNode(self.NodeCopyInventoryItem)
            self.NodeCopyInventoryItem = None

    pass
