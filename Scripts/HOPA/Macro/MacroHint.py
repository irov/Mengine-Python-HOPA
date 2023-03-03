from Foundation.GroupManager import GroupManager
from HOPA.Macro.MacroCommand import MacroCommand


class MacroHint(MacroCommand):
    def _onValues(self, values):
        pass

    def _onInitialize(self):
        if _DEVELOPMENT is True:
            if GroupManager.hasGroup("Hint") is False:
                self.initializeFailed("Hint group not found")

        Hint = GroupManager.getGroup("Hint")

        if _DEVELOPMENT is True:
            if Hint.hasObject("Demon_Hint") is False:
                self.initializeFailed("Hint group not have Demon_Hint")

        self.Demon_Hint = Hint.getObject("Demon_Hint")

    def _onGenerate(self, source):
        source.addTask("TaskHintClick", Hint=self.Demon_Hint)

