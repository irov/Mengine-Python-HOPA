from Foundation.ArrowManager import ArrowManager
from Foundation.Task.TaskAlias import TaskAlias

class AliasInventoryInvalidUseInventoryItemFX(TaskAlias):
    def _onParams(self, params):
        super(AliasInventoryInvalidUseInventoryItemFX, self)._onParams(params)

        self.Inventory = params.get("Inventory")
        pass

    def _onInitialize(self):
        super(AliasInventoryInvalidUseInventoryItemFX, self)._onInitialize()

        if _DEVELOPMENT is True:
            if ArrowManager.emptyArrowAttach() is True:
                self.initializeFailed("Attach not found")
                pass
            pass
        pass

    def _onGenerate(self, source):
        source.addTask("AliasInventoryReturnInventoryItemFX", Inventory=self.Inventory)
        pass

    pass