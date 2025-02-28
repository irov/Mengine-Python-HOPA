from Foundation.Task.TaskAlias import TaskAlias
from HOPA.EnigmaManager import EnigmaManager
from HOPA.HOGManager import HOGManager


class AliasHOGFoundItem(TaskAlias):
    def _onParams(self, params):
        super(AliasHOGFoundItem, self)._onParams(params)
        self.HOG = params.get("HOG")
        self.HOGItemName = params.get("HOGItemName")
        self.CrossOut = params.get("CrossOut", True)
        self.EnigmaName = params.get("EnigmaName")

    def _onGenerate(self, source):
        SceneName = EnigmaManager.getEnigmaSceneName(self.EnigmaName)
        GroupName = EnigmaManager.getEnigmaGroupName(self.EnigmaName)
        HOGItems = HOGManager.getHOGItems(self.EnigmaName)
        self.ItemName = HOGItems[self.HOGItemName].objectName
        HOGInventory = HOGManager.getInventory(self.EnigmaName)

        source.addTask("TaskHOGFoundItem", HOG=self.HOG, HOGItemName=self.HOGItemName)
        source.addNotify(Notificator.onHOGFoundItem, self.HOGItemName)

        source.addTask("TaskItemPick", ItemName=self.ItemName)

        with source.addParallelTask(2) as (tc_item, tc_inventory):
            tc_item.addTask("TaskHOGItemTakeEffect", ItemName=self.ItemName)

            tc_inventory.addTask("TaskHOGInventoryFoundItem", HOGInventory=HOGInventory, HOGItemName=self.HOGItemName)
            if self.CrossOut is True:
                tc_inventory.addTask("TaskHOGInventoryCrossOut", HOGItemName=self.HOGItemName, Immediately=False)
