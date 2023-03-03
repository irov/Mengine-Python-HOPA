from Foundation.ArrowManager import ArrowManager
from Foundation.Task.TaskAlias import TaskAlias


class AliasFittingInventoryReturnInventoryItem(TaskAlias):
    def _onParams(self, params):
        super(AliasFittingInventoryReturnInventoryItem, self)._onParams(params)
        self.FittingInventory = params.get("FittingInventory")

    def _onInitialize(self):
        super(AliasFittingInventoryReturnInventoryItem, self)._onInitialize()

        if _DEVELOPMENT is True:
            if ArrowManager.emptyArrowAttach() is True:
                self.initializeFailed("AliasFittingInventoryReturnInventoryItem Attach not found")

    def _onGenerate(self, source):
        InventoryItem = ArrowManager.getArrowAttach()

        ReturnSlotIndex = self.FittingInventory.getFittingIndex(InventoryItem)

        source.addTask("TaskRemoveArrowAttach")

        source.addTask("TaskEffectFittingInventoryReturnInventoryItem", FittingInventory=self.FittingInventory,
                       SlotID=ReturnSlotIndex, InventoryItem=InventoryItem)

        source.addTask("TaskFittingInventorySlotReturnItem", FittingInventory=self.FittingInventory,
                       SlotID=ReturnSlotIndex)
