from HOPA.DialogManager import DialogManager
from HOPA.Macro.MacroCommand import MacroCommand


class MacroDialog(MacroCommand):
    def _onValues(self, values):
        self.DialogID = values[0]
        pass

    def _onInitialize(self):
        if _DEVELOPMENT is True:
            if DialogManager.hasDialog(self.DialogID) is False:
                self.initializeFailed("DialogID %s not found" % (self.DialogID))
                pass
            pass
        pass

    def _onGenerate(self, source):
        Quest = self.addQuest(source, "Dialog", SceneName=self.SceneName, GroupName=self.GroupName,
                              DialogID=self.DialogID)

        with Quest as tc_quest:
            tc_quest.addTask("TaskSceneInit", SceneName=self.SceneName)
            tc_quest.addTask("AliasDialogPlay", DialogID=self.DialogID)
            pass
        pass

    pass
