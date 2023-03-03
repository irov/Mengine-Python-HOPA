from Foundation.GroupManager import GroupManager
from HOPA.Macro.MacroCommand import MacroCommand


class MacroPickReagentPaper(MacroCommand):
    def _onValues(self, values):
        self.itemName = values[0]
        pass

    def _onInitialize(self):
        pass

    def _onGenerate(self, source):
        ItemObject = GroupManager.getObject(self.GroupName, self.itemName)

        Quest = self.addQuest(source, "PickItem", SceneName=self.SceneName, GroupName=self.GroupName,
                              ItemName=self.itemName)

        with Quest as tc_quest:
            tc_quest.addTask("TaskItemClick", Item=ItemObject)
            pass
        source.addTask("AliasPickReagentPaper", ItemObject=ItemObject)
        pass

    pass
