from HOPA.Macro.MacroCommand import MacroCommand


class MacroDeactivateMagicVision(MacroCommand):
    def _onValues(self, values):
        pass

    def _onGenerate(self, source):
        source.addTask("AliasEnableMagicVision", Value=False)
        pass

    pass
