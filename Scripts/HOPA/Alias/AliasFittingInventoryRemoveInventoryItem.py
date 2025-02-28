from Foundation.Task.TaskAlias import TaskAlias


class AliasFittingInventoryRemoveInventoryItem(TaskAlias):
    def _onParams(self, params):
        super(AliasFittingInventoryRemoveInventoryItem, self)._onParams(params)

        self.FittingInventory = params.get("FittingInventory")
        self.InventoryItem = params.get("InventoryItem")

    def _onInitialize(self):
        super(AliasFittingInventoryRemoveInventoryItem, self)._onInitialize()

    def _onGenerate(self, source):
        source.addDisable(self.InventoryItem)
        source.addTask("TaskRemoveArrowAttach")

        source.addTask("TaskFittingInventoryRemoveInventoryItem", FittingInventory=self.FittingInventory,
                       InventoryItem=self.InventoryItem)

        FittingIndex = self.FittingInventory.getFittingIndex(self.InventoryItem)
        source.addTask("TaskFittingInventoryRemoveFitting", FittingInventory=self.FittingInventory,
                       FittingIndex=FittingIndex)
