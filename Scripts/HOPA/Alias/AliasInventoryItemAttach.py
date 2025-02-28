from Foundation.ArrowManager import ArrowManager
from Foundation.DemonManager import DemonManager
from Foundation.Task.MixinObjectTemplate import MixinInventoryItem
from Foundation.Task.TaskAlias import TaskAlias


class AliasInventoryItemAttach(MixinInventoryItem, TaskAlias):
    def _onCheck(self):
        if ArrowManager.emptyArrowAttach() is False:
            return False

        arrowItem = ArrowManager.getArrowAttach()

        if arrowItem is self.InventoryItem:
            return False

        Inventory = DemonManager.getDemon("Inventory")
        if Inventory.hasInventoryItem(self.InventoryItem) is False:
            self.log("Inventory not has inventoryItem%s" % (self.InventoryItem.getName()))
            return False

        return True

    def _onGenerate(self, source):
        source.addNotify(Notificator.onInventoryAttachInvItemToArrow, self.InventoryItem)
