from HOPA.Macro.MacroCommand import MacroCommand


class MacroMapSetMarkedDone(MacroCommand):
    def _onValues(self, values):
        self.SceneName = values[0]
        pass

    def _onInitialize(self):
        pass

    def _onGenerate(self, source):
        source.addNotify(Notificator.onMapMarked, self.SceneName)
        pass

    pass
