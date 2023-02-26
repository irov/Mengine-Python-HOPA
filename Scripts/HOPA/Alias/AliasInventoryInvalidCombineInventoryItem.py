from Foundation.ArrowManager import ArrowManager
from Foundation.Task.TaskAlias import TaskAlias

class AliasInventoryInvalidCombineInventoryItem(TaskAlias):
    def _onParams(self, params):
        super(AliasInventoryInvalidCombineInventoryItem, self)._onParams(params)

        self.Inventory = params.get("Inventory")
        pass

    def _onInitialize(self):
        super(AliasInventoryInvalidCombineInventoryItem, self)._onInitialize()

        if _DEVELOPMENT is True:
            if ArrowManager.emptyArrowAttach() is True:
                self.initializeFailed("Attach not found")
                pass
            pass
        pass

    def _onGenerate(self, source):
        #        source.addTask("TaskSoundEffect", SoundName = "CombineFailure", Wait = False)
        source.addTask("AliasInventoryReturnInventoryItem", Inventory=self.Inventory)
        pass

    pass