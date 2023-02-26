from Foundation.Task.Task import Task

class TaskFittingInventoryAddFitting(Task):
    def _onParams(self, params):
        super(TaskFittingInventoryAddFitting, self)._onParams(params)

        self.FittingInventory = params.get("FittingInventory")
        self.SlotIndex = params.get("SlotIndex")
        self.InventoryItem = params.get("InventoryItem")
        pass

    def _onInitialize(self):
        super(TaskFittingInventoryAddFitting, self)._onInitialize()
        pass

    def _onRun(self):
        self.FittingInventory.addFitting(self.SlotIndex, self.InventoryItem)

        return True
        pass
    pass