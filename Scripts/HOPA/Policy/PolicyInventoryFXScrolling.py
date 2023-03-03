from Foundation.DemonManager import DemonManager
from Foundation.Task.TaskAlias import TaskAlias
from HOPA.ItemManager import ItemManager


class PolicyInventoryFXScrolling(TaskAlias):
    def _onParams(self, params):
        super(PolicyInventoryFXScrolling, self)._onParams(params)
        self.Inventory = DemonManager.getDemon("Inventory")
        self.InventoryItem = params.get("InventoryItem")
        pass

    def _onGenerate(self, source):
        def __thisItem(action, inventory, invItem, itemName):
            if self.InventoryItem != invItem:
                return False
                pass
            return True
            pass

        ItemName = ItemManager.getInventoryItemKey(self.InventoryItem)

        with source.addParallelTask(2) as (tc1, tc2):
            tc1.addTask("TaskListener", ID=Notificator.onInventoryFXActionEnd, Filter=__thisItem)
            tc2.addTask("TaskNotify", ID=Notificator.onItemClickToInventory,
                        Args=(self.Inventory, ItemName, "ActionHintUse"))
            pass

        pass

    pass
