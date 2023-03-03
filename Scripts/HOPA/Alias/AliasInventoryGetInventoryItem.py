from Foundation.DemonManager import DemonManager
from Foundation.Task.TaskAlias import TaskAlias
from HOPA.ItemManager import ItemManager


class AliasInventoryGetInventoryItem(TaskAlias):
    def _onParams(self, params):
        super(AliasInventoryGetInventoryItem, self)._onParams(params)
        self.ItemName = params.get("ItemName")
        self.Inventory = DemonManager.getDemon("Inventory")
        pass

    def _onCheck(self):
        InventoryItem = ItemManager.getItemInventoryItem(self.ItemName)
        if self.Inventory.hasInventoryItem(InventoryItem) is True:
            if self.ItemName in InventoryItem.getFoundItems():
                return False
            return True
        return True

    def _onSkip(self):
        super(AliasInventoryGetInventoryItem, self)._onSkip()
        pass

    def _onGenerate(self, source):
        InventoryItem = ItemManager.getItemInventoryItem(self.ItemName)

        source.addTask("TaskNotify", ID=Notificator.onItemPopUp, Args=(self.ItemName,))

        def __isItem(inventory, invItem):
            if InventoryItem is not invItem:
                return False

            return True

        source.addTask("TaskListener", ID=Notificator.onGetItem, Filter=__isItem)
