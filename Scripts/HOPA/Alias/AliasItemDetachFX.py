from Foundation.ArrowManager import ArrowManager
from Foundation.DemonManager import DemonManager
from Foundation.Task.MixinObjectTemplate import MixinInventoryItem
from Foundation.Task.TaskAlias import TaskAlias


class AliasItemDetachFX(MixinInventoryItem, TaskAlias):
    def _onParams(self, params):
        super(AliasItemDetachFX, self)._onParams(params)
        self.Inventory = DemonManager.getDemon("Inventory")
        self.Return = params.get("Return", True)

    def _onCheck(self):
        if ArrowManager.emptyArrowAttach() is True:
            return False

        arrowItem = ArrowManager.getArrowAttach()

        if arrowItem == self.InventoryItem:
            return True

        return False

    def _onGenerate(self, source):
        source.addTask("AliasInventoryReturnInventoryItemFX", Inventory=self.Inventory, UnblockInventory=True,
                       Return=self.Return)
