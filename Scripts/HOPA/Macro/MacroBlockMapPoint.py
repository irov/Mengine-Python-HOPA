from HOPA.Macro.MacroCommand import MacroCommand


class MacroBlockMapPoint(MacroCommand):
    def _onValues(self, values):
        self.SceneName = values[0]

    def _onGenerate(self, source):
        source.addNotify(Notificator.onMapPointBlock, self.SceneName)
