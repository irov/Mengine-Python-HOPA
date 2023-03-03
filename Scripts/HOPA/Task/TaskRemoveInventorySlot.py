from Foundation.Task.Task import Task


class TaskAppendInventorySlot(Task):
    Skiped = True

    def _onParams(self, params):
        super(TaskAppendInventorySlot, self)._onParams(params)

        self.Inventory = params.get("Inventory")
        self.ItemName = params.get("ItemName")

    def _onInitialize(self):
        super(TaskAppendInventorySlot, self)._onInitialize()

    def _onRun(self):
        # Create slot auto append in inventory
        self.Inventory.createSlot(self.ItemName)
        return True
