from Foundation.Task.Task import Task


class TaskFittingInventoryRemoveInventoryItem(Task):
    Skiped = True

    def _onParams(self, params):
        super(TaskFittingInventoryRemoveInventoryItem, self)._onParams(params)

        self.FittingInventory = params.get("FittingInventory")
        self.InventoryItem = params.get("InventoryItem")
        pass

    def _onInitialize(self):
        super(TaskFittingInventoryRemoveInventoryItem, self)._onInitialize()
        pass

    def _onRun(self):
        self.FittingInventory.removeInventoryItem(self.InventoryItem)
        slotID = self.FittingInventory.getInventoryItemSlotIndex(self.InventoryItem)
        FittingInventoryInventoryEntity = self.FittingInventory.getEntity()

        slots = FittingInventoryInventoryEntity.getSlots()
        slot = slots[slotID]

        slot.removeItem()
        return True
        pass

    pass
