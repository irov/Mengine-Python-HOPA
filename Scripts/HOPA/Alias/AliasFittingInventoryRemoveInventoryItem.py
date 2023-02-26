from Foundation.Task.TaskAlias import TaskAlias

class AliasFittingInventoryRemoveInventoryItem(TaskAlias):
    def _onParams(self, params):
        super(AliasFittingInventoryRemoveInventoryItem, self)._onParams(params)

        self.FittingInventory = params.get("FittingInventory")
        self.InventoryItem = params.get("InventoryItem")

        pass

    def _onInitialize(self):
        super(AliasFittingInventoryRemoveInventoryItem, self)._onInitialize()
        pass

    def _onGenerate(self, source):
        source.addTask("TaskEnable", Object=self.InventoryItem, Value=False)
        source.addTask("TaskRemoveArrowAttach")

        source.addTask("TaskFittingInventoryRemoveInventoryItem", FittingInventory=self.FittingInventory, InventoryItem=self.InventoryItem)

        FittingIndex = self.FittingInventory.getFittingIndex(self.InventoryItem)
        source.addTask("TaskFittingInventoryRemoveFitting", FittingInventory=self.FittingInventory, FittingIndex=FittingIndex)
        pass

    pass