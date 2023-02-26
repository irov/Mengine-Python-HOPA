from Foundation.Task.TaskAlias import TaskAlias

from HOPA.QuestManager import QuestManager

class AliasJournalAddItemPage(TaskAlias):
    def _onParams(self, params):
        super(AliasJournalAddItemPage, self)._onParams(params)
        self.SceneName = params.get("SceneName")
        self.ItemObject = params.get("ItemObject")
        pass

    def _onGenerate(self, source):
        Quest = QuestManager.createLocalQuest("PickItem", SceneName=self.SceneName, GroupName=self.GroupName, ItemName=self.ItemObject.name)

        with QuestManager.runQuest(source, Quest) as tc_quest:
            tc_quest.addTask("TaskItemClick", Item=self.ItemObject)
            pass

        source.addTask("TaskEnable", Object=self.ItemObject, Value=False)

        pass

    pass