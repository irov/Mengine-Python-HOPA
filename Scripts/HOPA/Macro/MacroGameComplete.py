from HOPA.Macro.MacroCommand import MacroCommand

class MacroGameComplete(MacroCommand):
    def _onValues(self, values):
        pass

    def _onInitialize(self):
        pass

    def _onGenerate(self, source):
        # source.addTask("TaskFunction", Fn = Mengine.changeCurrentAccountSetting, Args = ("IsBonusChapter", u"2"))
        source.addTask("TaskFunction", Fn=Mengine.changeCurrentAccountSetting, Args=("GameComplete", u"True"))
        source.addTask("TaskNotify", ID=Notificator.onGameComplete)
        pass
    pass