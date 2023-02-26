from HOPA.Macro.MacroCommand import MacroCommand

class MacroSetHintReloading(MacroCommand):
    def _onValues(self, values):
        self.Value = values[0]
        pass

    def _onInitialize(self):
        pass

    def _onGenerate(self, source):
        source.addNotify(Notificator.onSetReloading, self.GroupName)
        pass
    pass