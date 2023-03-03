from HOPA.Macro.MacroCommand import MacroCommand


class MacroUnblockMapHog(MacroCommand):
    def _onValues(self, values):
        self.HogID = values[0]
        pass

    def _onGenerate(self, source):
        source.addTask("TaskNotify", ID=Notificator.onMapHogUnblock, Args=(self.HogID,))
        pass

    pass
