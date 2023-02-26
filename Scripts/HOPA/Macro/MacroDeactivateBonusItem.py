from HOPA.Macro.MacroCommand import MacroCommand

class MacroDeactivateBonusItem(MacroCommand):
    def _onValues(self, values):
        pass

    def _onGenerate(self, source):
        source.addTask("TaskEnableBonusItem", Value=False)
        pass
    pass