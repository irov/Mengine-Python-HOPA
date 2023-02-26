from Foundation.ArrowManager import ArrowManager
from Foundation.Task.TaskAlias import TaskAlias

class AliasFittingInventoryInvalidUseInventoryItem(TaskAlias):
    def _onParams(self, params):
        super(AliasFittingInventoryInvalidUseInventoryItem, self)._onParams(params)

        self.FittingInventory = params.get("FittingInventory")
        pass

    def _onInitialize(self):
        super(AliasFittingInventoryInvalidUseInventoryItem, self)._onInitialize()

        if _DEVELOPMENT is True:
            if ArrowManager.emptyArrowAttach() is True:
                self.initializeFailed("Attach not found")
                pass
            pass
        pass

    def _onGenerate(self, source):
        source.addTask("TaskSoundEffect", SoundName="Wrong", Wait=False)
        source.addTask("AliasFittingInventoryReturnInventoryItem", FittingInventory=self.FittingInventory)
        pass

    pass