from Foundation.ArrowManager import ArrowManager
from Foundation.Task.TaskAlias import TaskAlias


class AliasFittingInventoryInvalidCombineInventoryItem(TaskAlias):
    def _onParams(self, params):
        super(AliasFittingInventoryInvalidCombineInventoryItem, self)._onParams(params)

        self.FittingInventory = params.get("FittingInventory")
        pass

    def _onInitialize(self):
        super(AliasFittingInventoryInvalidCombineInventoryItem, self)._onInitialize()

        if _DEVELOPMENT is True:
            if ArrowManager.emptyArrowAttach() is True:
                self.initializeFailed("Attach not found")

    def _onGenerate(self, source):
        source.addTask("TaskSoundEffect", SoundName="CombineFailure", Wait=False)
        source.addTask("AliasFittingInventoryReturnInventoryItem", FittingInventory=self.FittingInventory)
