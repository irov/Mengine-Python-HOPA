from HOPA.Macro.MacroCommand import MacroCommand
from HOPA.TutorialManager import TutorialManager


class MacroTutorialOpen(MacroCommand):
    def _onValues(self, values):
        self.TutorName = values[0]
        pass

    def _onInitialize(self):
        if _DEVELOPMENT is True:
            if TutorialManager.hasEntry(self.TutorName) is False:
                self.initializeFailed(" %s doesnt exist object " % self.TutorName)
        pass

    def _onGenerate(self, source):
        source.addTask("TaskNotify", ID=Notificator.onTutorialShow, Args=(self.TutorName,))
        pass
