from HOPA.Macro.MacroCommand import MacroCommand

from HOPA.StageManager import StageManager


class MacroRunStage(MacroCommand):
    def _onValues(self, values):
        self.StageName = values[0]
        pass

    def _onInitialize(self):
        if _DEVELOPMENT is True:
            if StageManager.hasStage(self.StageName) is None:
                self.initializeFailed("Stage %s not found" % (self.StageName))
                pass
            pass
        pass

    def _onGenerate(self, source):
        source.addTask("AliasStageRun", StageName=self.StageName)
        pass

    pass
