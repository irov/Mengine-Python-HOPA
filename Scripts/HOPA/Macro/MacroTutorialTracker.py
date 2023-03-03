from HOPA.Macro.MacroCommand import MacroCommand


class MacroTutorialTracker(MacroCommand):
    def _onValues(self, values):
        self.value_0 = values[0]
        self.value_1 = values[1]
        pass

    def _onInitialize(self):
        pass

    def _onGenerate(self, source):
        source.addNotify(Notificator.onTutorialProgres, self.value_1, self.value_0, self.GroupName)

    pass
