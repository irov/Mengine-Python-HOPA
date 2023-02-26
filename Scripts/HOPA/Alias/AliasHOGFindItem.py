from Foundation.Task.TaskAlias import TaskAlias
from HOPA.EnigmaManager import EnigmaManager
from HOPA.HOGManager import HOGManager
from HOPA.QuestManager import QuestManager

class AliasHOGFindItem(TaskAlias):
    def _onParams(self, params):
        super(AliasHOGFindItem, self)._onParams(params)
        self.HOG = params.get("HOG")
        self.HOGItemName = params.get("HOGItemName")
        self.CrossOut = params.get("CrossOut", True)
        self.EnigmaName = params.get("EnigmaName")
        pass

    def _onGenerate(self, source):
        SceneName = EnigmaManager.getEnigmaSceneName(self.EnigmaName)
        GroupName = EnigmaManager.getEnigmaGroupName(self.EnigmaName)
        hogItem = HOGManager.getHOGItem(self.EnigmaName, self.HOGItemName)
        ItemName = hogItem.objectName

        HOGInventory = HOGManager.getInventory(self.EnigmaName)

        Quest = QuestManager.createLocalQuest("HOGPickItem", SceneName=SceneName, GroupName=GroupName, HogGroupName=self.GroupName, ItemName=ItemName)

        with QuestManager.runQuest(source, Quest) as tc_quest:
            tc_quest.addTask("TaskItemClick", ItemName=ItemName)
            pass

        source.addTask("TaskHOGFoundItem", HOG=self.HOG, HOGItemName=self.HOGItemName)
        source.addTask("TaskNotify", ID=Notificator.onHOGFoundItem, Args=(self.HOGItemName,))

        source.addTask("TaskItemPick", ItemName=ItemName)

        with source.addParallelTask(2) as (tc_item, tc_inventory):
            tc_item.addTask("TaskHOGItemTakeEffect", ItemName=ItemName)

            tc_inventory.addTask("TaskHOGInventoryFoundItem", HOGInventory=HOGInventory, HOGItemName=self.HOGItemName)
            if self.CrossOut is True:
                tc_inventory.addTask("TaskHOGInventoryCrossOut", HOGItemName=self.HOGItemName, Immediately=False)
                pass
            pass
        pass

    pass