from Foundation.Task.Task import Task


class TaskFittingInventoryAddInventoryItem(Task):
    Skiped = True

    def _onParams(self, params):
        super(TaskFittingInventoryAddInventoryItem, self)._onParams(params)

        self.FittingInventory = params.get("FittingInventory")
        self.InventoryItem = params.get("InventoryItem")
        pass

    def _onInitialize(self):
        super(TaskFittingInventoryAddInventoryItem, self)._onInitialize()
        pass

    def _onRun(self):
        self.FittingInventory.addInventoryItem(self.InventoryItem)

        return True
        pass

    pass
