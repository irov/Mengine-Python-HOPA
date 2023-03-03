from HOPA.Macro.MacroCommand import MacroCommand


class MacroDelay(MacroCommand):
    def _onValues(self, values):
        self.Time = float(values[0]) * 1000.0
        pass

    def _onGenerate(self, source):
        source.addTask("TaskDelay", Time=self.Time)
        pass

    pass
