from Foundation.Task.Task import Task


class TaskFittingInventorySlotReturnItem(Task):
    def __init__(self):
        super(TaskFittingInventorySlotReturnItem, self).__init__()
        pass

    def _onParams(self, params):
        super(TaskFittingInventorySlotReturnItem, self)._onParams(params)

        self.FittingInventory = params.get("FittingInventory")
        self.SlotID = params.get("SlotID", None)
        pass

    def _onInitialize(self):
        super(TaskFittingInventorySlotReturnItem, self)._onInitialize()
        pass

    def _onRun(self):
        FittingInventoryEntity = self.FittingInventory.getEntity()

        slots = FittingInventoryEntity.getSlots()

        slot = slots[self.SlotID]
        slot.returnItem()

        return True
        pass

    pass
