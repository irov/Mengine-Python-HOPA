from HOPA.Macro.MacroCommand import MacroCommand

class MacroFittFind(MacroCommand):
    def _onValues(self, values):
        self.ItemName = values[0]
        pass

    def _onGenerate(self, source):
        #        item = GroupManager(self.GroupName,self.ItemName)
        #        Quest = self.addQuest(source, "PickItem", SceneName = self.SceneName, GroupName = self.GroupName, ItemName = self.ItemName)
        #        with QuestManager.runQuest(source, Quest) as tc_quest:
        source.addTask("AliasFittingFindItem", SceneName=self.SceneName, ItemName=self.ItemName)
        pass
    pass