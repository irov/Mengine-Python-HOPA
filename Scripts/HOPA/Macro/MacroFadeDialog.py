from HOPA.DialogManager import DialogManager
from HOPA.Macro.MacroCommand import MacroCommand


class MacroFadeDialog(MacroCommand):
    def _onValues(self, values):
        self.DialogID = values[0]

    def _onInitialize(self):
        if _DEVELOPMENT is True:
            if DialogManager.hasDialog(self.DialogID) is False:
                self.initializeFailed("DialogID %s not found" % (self.DialogID))

    def _onGenerate(self, source):
        if self.SceneName is not None:
            source.addTask("TaskSceneActivate")

        source.addTask("AliasDialogPlay", DialogID=self.DialogID, Fade=False)

