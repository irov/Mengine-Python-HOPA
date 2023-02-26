from HOPA.Macro.MacroCommand import MacroCommand

class MacroBlockInput(MacroCommand):
    def _onValues(self, values):
        pass

    def _onInitialize(self):
        pass

    def _onGenerate(self, source):
        source.addNotify(Notificator.onBlockInput, True)