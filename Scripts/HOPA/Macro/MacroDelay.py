from HOPA.Macro.MacroCommand import MacroCommand
from HOPA.QuestManager import QuestManager


class MacroDelay(MacroCommand):
    def _onValues(self, values):
        self.Time = float(values[0]) * 1000.0
        pass

    def _onGenerate(self, source):
        if QuestManager.hasQuestType("Delay") is False:
            source.addDelay(self.Time)
            return

        quest = self.addQuest(source, "Delay", SceneName=self.SceneName, GroupName=self.GroupName, Duration=self.Time)
        with quest as tc_quest:
            tc_quest.addDelay(self.Time)
        pass

    pass
