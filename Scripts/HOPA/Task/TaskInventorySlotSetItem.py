import Trace
from Foundation.Task.MixinObjectTemplate import MixinInventoryItem
from Foundation.Task.Task import Task

class TaskInventorySlotSetItem(MixinInventoryItem, Task):
    Skiped = True

    def _onParams(self, params):
        super(TaskInventorySlotSetItem, self)._onParams(params)
        self.Inventory = params.get("Inventory")
        self.SlotID = params.get("SlotID", None)
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

        slots = InventoryEntity.getSlots()
        if self.SlotID >= len(slots):
            # Trace.log("TaskInventorySlotSetItem", 0, "TaskInventorySlotSetItem._onCheck trying ti get Slot %s, but Inventory size is %s (lesser)"%(self.SlotID, len(slots)))
            Trace.log("Entity", 0, "TaskInventorySlotSetItem._onCheck trying ti get Slot %s, but Inventory size is %s (lesser)" % (self.SlotID, len(slots)))
            return False
            pass

        slot = slots[self.SlotID]

        if slot.empty() is False:
            return False
            pass

        return True
        pass

    def _onRun(self):
        InventoryEntity = self.Inventory.getEntity()

        slots = InventoryEntity.getSlots()

        slot = slots[self.SlotID]

        slot.setItem(self.InventoryItem)

        return True
        pass

    pass