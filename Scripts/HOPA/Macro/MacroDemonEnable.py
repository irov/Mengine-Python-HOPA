from Foundation.DemonManager import DemonManager
from HOPA.Macro.MacroCommand import MacroCommand


class MacroDemonEnable(MacroCommand):
    def _onValues(self, values):
        self.DemonName = values[0]
        pass

    def _onGenerate(self, source):
        Demon = DemonManager.getDemon(self.DemonName)

        source.addTask("TaskEnable", Object=Demon, Value=True)
        pass

    pass
