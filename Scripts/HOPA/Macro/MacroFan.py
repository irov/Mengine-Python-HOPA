from HOPA.FanManager import FanManager
from HOPA.Macro.MacroCommand import MacroCommand

class MacroFan(MacroCommand):
    def _onValues(self, values):
        self.FanName = values[0]
        pass

    def _onInitialize(self):
        if _DEVELOPMENT is True:
            if FanManager.hasFan(self.FanName) is False:
                self.initializeFailed("Fan %s not found" % (self.HOGName))
                pass
            pass
        pass

    def _onGenerate(self, source):
        source.addTask("AliasFanPlay", FanName=self.FanName)
        pass
    pass