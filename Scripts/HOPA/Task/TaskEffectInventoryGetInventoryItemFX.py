from Foundation.DefaultManager import DefaultManager
from Foundation.GroupManager import GroupManager
from Foundation.SceneManager import SceneManager
from Foundation.Task.TaskAlias import TaskAlias
from HOPA.ItemManager import ItemManager

class TaskEffectInventoryGetInventoryItemFX(TaskAlias):
    def _onParams(self, params):
        super(TaskEffectInventoryGetInventoryItemFX, self)._onParams(params)

        self.Inventory = params.get("Inventory")
        self.ItemName = params.get("ItemName")
        pass

    def _onCheck(self):
        if self.Inventory.isActive() is False:
            return False
            pass

        InventoryEntity = self.Inventory.getEntity()

        if InventoryEntity.isActivate() is False:
            return False
            pass

        return True
        pass

    def _onGenerate(self, source):
        InventoryItem = ItemManager.getItemInventoryItem(self.ItemName)

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
        if len(InvItemFoundItems) <= 1:
            InventoryItem.setEnable(False)
            slot.hotspot.disable()
            pass

        point = slot.getPoint()

        Camera = Mengine.getRenderCamera2D()
        P2 = Mengine.getCameraPosition(Camera, point)

        scene = SceneManager.getCurrentScene()
        layer_InventoryItemEffect = scene.getSlot("InventoryItemEffect")

        InventoryItemEntityNode = InventoryItem.getEntityNode()

        layer_InventoryItemEffect.addChild(InventoryItemEntityNode)

        GroupPopUp = GroupManager.getGroup("ItemPopUp")
        Demon_ItemPopUp = GroupPopUp.getObject("Demon_ItemPopUp")
        Point_Item = Demon_ItemPopUp.getObject("Point_Item")

        Point_ItemEntity = Point_Item.getEntity()
        P0 = Point_ItemEntity.getCameraPosition(Camera)
        P1 = (P2[0], P0[1])

        source.addTask("TaskObjectSetPosition", Object=InventoryItem, Value=P0)
        source.addTask("TaskEnable", Object=InventoryItem, Value=True)

        SpeedEffectInventoryGetInventoryItem = DefaultManager.getDefaultFloat("SpeedEffectInventoryGetInventoryItem", 1000.0)
        SpeedEffectInventoryGetInventoryItem *= 0.001  # speed fix
        source.addTask("TaskNodeBezier2To", Node=InventoryItemEntityNode, Point1=P1, To=P2, Speed=SpeedEffectInventoryGetInventoryItem)

        source.addTask("TaskNodeRemoveFromParent", Node=InventoryItemEntityNode)

        def __slotSetItem(slot):
            slot.setItem(InventoryItem)
            pass

        source.addTask("TaskFunction", Fn=__slotSetItem, Args=(slot,))
        source.addTask("TaskNodeEnable", Node=InventoryItemEntityNode, Value=True)

        return False
        pass
    pass