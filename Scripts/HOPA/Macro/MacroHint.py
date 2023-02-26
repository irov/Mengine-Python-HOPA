from Foundation.GroupManager import GroupManager
from HOPA.Macro.MacroCommand import MacroCommand

class MacroHint(MacroCommand):
    def _onValues(self, values):
        pass

    def _onInitialize(self):
        if _DEVELOPMENT is True:
            if GroupManager.hasGroup("Hint") is False:
                self.initializeFailed("Hint group not found")
                pass
            pass

        Hint = GroupManager.getGroup("Hint")

        if _DEVELOPMENT is True:
            if Hint.hasObject("Demon_Hint") is False:
                self.initializeFailed("Hint group not have Demon_Hint")
                pass
            pass

        self.Demon_Hint = Hint.getObject("Demon_Hint")
        pass

    def _onGenerate(self, source):
        source.addTask("TaskHintClick", Hint=self.Demon_Hint)
        pass
    pass