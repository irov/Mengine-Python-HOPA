from HOPA.Macro.MacroCommand import MacroCommand


class MacroTutorialFadeHide(MacroCommand):

    def _onValues(self, values):
        # self.MovieID = values[0]
        pass

    def _onInitialize(self):
        pass

    def _onGenerate(self, source):
        source.addTask("TaskNotify", ID=Notificator.onTutorialFadeHide)
        pass
