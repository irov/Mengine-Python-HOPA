from Foundation.ArrowManager import ArrowManager
from Foundation.Task.TaskAlias import TaskAlias

class AliasInventoryInvalidUseInventoryItem(TaskAlias):
    def _onParams(self, params):
        super(AliasInventoryInvalidUseInventoryItem, self)._onParams(params)

        self.Inventory = params.get("Inventory")
        pass

    def _onInitialize(self):
        super(AliasInventoryInvalidUseInventoryItem, self)._onInitialize()

        if _DEVELOPMENT is True:
            if ArrowManager.emptyArrowAttach() is True:
                self.initializeFailed("Attach not found")
                pass
            pass
        pass

    def _onGenerate(self, source):
        source.addTask("AliasInventoryReturnInventoryItem", Inventory=self.Inventory)
        pass

    pass