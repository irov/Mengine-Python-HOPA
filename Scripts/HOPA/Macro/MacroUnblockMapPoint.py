from HOPA.Macro.MacroCommand import MacroCommand


class MacroUnblockMapPoint(MacroCommand):
    def _onValues(self, values):
        self.SceneName = values[0]
        pass

    def _onGenerate(self, source):
        source.addTask("TaskNotify", ID=Notificator.onMapPointUnblock, Args=(self.SceneName,))
        pass

    pass
