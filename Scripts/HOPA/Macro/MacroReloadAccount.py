from HOPA.Macro.MacroCommand import MacroCommand


class MacroReloadAccount(MacroCommand):
    def _onValues(self, values):
        pass

    def _onGenerate(self, source):
        source.addTask("TaskNotify", ID=Notificator.onReloadAccount)
        pass

    pass
