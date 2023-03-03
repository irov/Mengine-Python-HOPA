from HOPA.Macro.MacroCommand import MacroCommand

from HOPA.MindManager import MindManager


class MacroMind(MacroCommand):
    def _onValues(self, values):
        self.MindID = values[0]
        self.Static = False
        if len(values) > 1:
            self.Static = bool(values[1])

    def _onInitialize(self):
        if _DEVELOPMENT is True:
            if MindManager.hasMind(self.MindID) is False:
                self.initializeFailed("Mind %s not found" % (self.MindID))
                pass
            pass
        pass

    def _onGenerate(self, source):
        isZoom = self.ScenarioRunner.isZoom
        source.addTask("AliasMindPlay", MindID=self.MindID, isZoom=isZoom, Static=self.Static)
        pass

    pass
