from Foundation.Task.Task import Task

class TaskInventoryCurrentSlotIndex(Task):
    Skiped = True

    def __init__(self):
        super(TaskInventoryCurrentSlotIndex, self).__init__()
        pass

    def _onParams(self, params):
        super(TaskInventoryCurrentSlotIndex, self)._onParams(params)
        self.Inventory = params.get("Inventory")
        self.Value = params.get("Value")
        pass

    def _onInitialize(self):
        super(TaskInventoryCurrentSlotIndex, self)._onInitialize()
        pass

    def _onRun(self):
        currentIndex = self.Inventory.getParam("CurrentSlotIndex")
        if currentIndex == self.Value:
            return True
            pass

        self.Inventory.setParam("CurrentSlotIndex", self.Value)

        return True
        pass
    pass