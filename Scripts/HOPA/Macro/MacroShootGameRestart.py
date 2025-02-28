from HOPA.Macro.MacroCommand import MacroCommand


class MacroShootGameRestart(MacroCommand):
    def _onValues(self, values):
        pass

    def _onGenerate(self, source):
        source.addListener(Notificator.onShootGameRestart)
        pass

    pass
