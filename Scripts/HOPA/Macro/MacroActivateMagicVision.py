from HOPA.Macro.MacroCommand import MacroCommand

class MacroActivateMagicVision(MacroCommand):
    def _onValues(self, values):
        pass

    def _onGenerate(self, source):
        source.addTask("AliasEnableMagicVision", Value=True)
        pass
    pass