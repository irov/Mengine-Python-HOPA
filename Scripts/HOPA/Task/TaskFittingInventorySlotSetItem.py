from Foundation.Task.Task import Task


class TaskFittingInventorySlotSetItem(Task):
    def __init__(self):
        super(TaskFittingInventorySlotSetItem, self).__init__()
        pass

    def _onParams(self, params):
        super(TaskFittingInventorySlotSetItem, self)._onParams(params)

        self.FittingInventory = params.get("FittingInventory")
        self.InventoryItem = params.get("InventoryItem")
        self.SlotID = params.get("SlotID", None)
        pass

    def _onInitialize(self):
        super(TaskFittingInventorySlotSetItem, self)._onInitialize()
        pass

    def _onRun(self):
        FittingInventoryEntity = self.FittingInventory.getEntity()

        slots = FittingInventoryEntity.getSlots()

        slot = slots[self.SlotID]

        slot.setItem(self.InventoryItem)

        return True
        pass

    pass
