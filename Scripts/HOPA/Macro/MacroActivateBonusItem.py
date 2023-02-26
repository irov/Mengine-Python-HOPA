from HOPA.Macro.MacroCommand import MacroCommand

class MacroActivateBonusItem(MacroCommand):
    def _onValues(self, values):
        pass

    def _onGenerate(self, source):
        source.addTask("TaskEnableBonusItem", Value=True)
        pass
    pass