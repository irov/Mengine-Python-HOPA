from HOPA.DialogBoxManager import DialogBoxManager
from HOPA.Macro.MacroCommand import MacroCommand


class MacroDialogBox(MacroCommand):
    def _onValues(self, values):
        self.DialogID = values
        pass

    def _onInitialize(self):
        if _DEVELOPMENT is True:
            for id in self.DialogID:
                if DialogBoxManager.hasDialog(id) is False:
                    self.initializeFailed("DialogBox dialog %s not found" % (id))
                    pass
                pass
            pass
        pass

    def _onGenerate(self, source):
        Quest = self.addQuest(source, "DialogBox", SceneName=self.SceneName, GroupName=self.GroupName,
                              DialogID=self.DialogID)

        with Quest as tc_quest:
            tc_quest.addTask("AliasDialogBoxPlay", DialogID=self.DialogID)

        # source.addTask("AliasDialogBoxPlay", DialogID=self.DialogID)
        # source.addListener(Notificator.onDialogBoxPlayComplete, Filter=lambda ID: ID is self.DialogID)

        pass

    pass
