from Foundation.Task.MixinObjectTemplate import MixinInventoryItem
from Foundation.Task.Task import Task

class TaskInventorySlotReturnItemFX(MixinInventoryItem, Task):
    Skiped = True

    def _onParams(self, params):
        super(TaskInventorySlotReturnItemFX, self)._onParams(params)
        self.Inventory = params.get("Inventory")
        self.SetSlotIndex = None
        pass

    def _onCheck(self):
        if self.Inventory.isActive() is False:
            return False
            pass

        if self.Inventory.hasInventoryItem(self.InventoryItem) is False:
            return False
            pass

        InventoryEntity = self.Inventory.getEntity()

        if InventoryEntity.isActivate() is False:
            return False
            pass

        CurrentSlotIndex = self.Inventory.getParam("CurrentSlotIndex")
        InventoryItems = self.Inventory.getParam("InventoryItems")

        InventoryItemReturnIndex = InventoryItems.index(self.InventoryItem)

        self.SetSlotIndex = InventoryItemReturnIndex - CurrentSlotIndex

        slots = InventoryEntity.getSlots()

        if len(slots) <= self.SetSlotIndex:
            return False

        slot = slots[self.SetSlotIndex]

        if slot.empty() is False:
            return False
            pass

        return True
        pass

    def _onRun(self):
        InventoryEntity = self.Inventory.getEntity()

        slots = InventoryEntity.getSlots()

        slot = slots[self.SetSlotIndex]

        slot.cursorItem = None
        slot.setItem(self.InventoryItem)

        return True
        pass

    pass