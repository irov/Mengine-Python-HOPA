from HOPA.Macro.MacroCommand import MacroCommand

class MacroTutorialClose(MacroCommand):
    def _onGenerate(self, source):
        source.addTask("TaskNotify", ID=Notificator.onTutorialHide)
        pass