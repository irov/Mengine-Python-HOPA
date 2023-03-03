from Foundation.DemonManager import DemonManager
from HOPA.Macro.MacroCommand import MacroCommand


class MacroSetSkipReloading(MacroCommand):
    def _onValues(self, values):
        self.Value = values[0]
        pass

    def _onInitialize(self):
        pass

    def _onGenerate(self, source):
        source.addFunction(self._Run_Macro)
        pass

    def _Run_Macro(self):
        DemonSkipPuzzle = DemonManager.getDemon('SkipPuzzle')
        DemonSkipPuzzle.setParam("ForceReload", self.Value)
        pass

    pass
