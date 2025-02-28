from HOPA.Macro.MacroCommand import MacroCommand


class MacroAwardsOpen(MacroCommand):
    def _onValues(self, values):
        self.awardsId = values[0]

    def _onGenerate(self, source):
        source.addNotify(Notificator.onAwardsOpen, self.awardsId)
