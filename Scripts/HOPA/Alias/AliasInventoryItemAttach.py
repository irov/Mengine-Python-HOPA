from Foundation.ArrowManager import ArrowManager
from Foundation.DemonManager import DemonManager
from Foundation.Task.MixinObjectTemplate import MixinInventoryItem
from Foundation.Task.TaskAlias import TaskAlias

class AliasInventoryItemAttach(MixinInventoryItem, TaskAlias):
    def _onCheck(self):
        if ArrowManager.emptyArrowAttach() is False:
            return False
            pass

        arrowItem = ArrowManager.getArrowAttach()

        if arrowItem is self.InventoryItem:
            return False
            pass

        Inventory = DemonManager.getDemon("Inventory")
        if Inventory.hasInventoryItem(self.InventoryItem) is False:
            self.log("Inventory not has inventoryItem%s" % (self.InventoryItem.getName()))
            return False
            pass

        return True
        pass

    def _onGenerate(self, source):
        source.addTask("TaskNotify", ID=Notificator.onInventoryAttachInvItemToArrow, Args=(self.InventoryItem,))
        pass
    pass