from HOPA.Macro.MacroCommand import MacroCommand

class MacroDecreaseMana(MacroCommand):
    def _onValues(self, values):
        self.Value = values[0]
        pass

    def _onGenerate(self, source):
        source.addTask("TaskNotify", ID=Notificator.onManaDecrease, Args=(self.Value,))
        pass
    pass