from Foundation.Task.Task import Task

class TaskFittingInventoryRemoveFitting(Task):
    Skiped = True

    def _onParams(self, params):
        super(TaskFittingInventoryRemoveFitting, self)._onParams(params)

        self.FittingInventory = params.get("FittingInventory")
        self.FittingIndex = params.get("FittingIndex")
        pass

    def _onInitialize(self):
        super(TaskFittingInventoryRemoveFitting, self)._onInitialize()
        pass

    def _onRun(self):
        self.FittingInventory.removeFitting(self.FittingIndex)

        return True
        pass
    pass