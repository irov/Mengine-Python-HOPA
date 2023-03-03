from HOPA.Macro.MacroCommand import MacroCommand

from HOPA.SemaphoreManager import SemaphoreManager


class MacroWaitSemaphore(MacroCommand):
    def _onValues(self, values):
        self.Name = values[0]
        self.From = values[1]

        if len(values) == 3:
            self.To = values[2]

        else:
            self.To = None

    def _onInitialize(self):
        self.isTechnical = True

    def _onGenerate(self, source):
        Quest = self.addQuest(source, "WaitSemaphore", SceneName=self.SceneName, GroupName=self.GroupName,
                              Name=self.Name, From=self.From, To=self.To)

        Semaphore = SemaphoreManager.getSemaphore(self.Name)

        with Quest as tc_quest:
            tc_quest.addSemaphore(Semaphore, From=self.From, To=self.To)
