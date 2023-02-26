from HOPA.Macro.MacroCommand import MacroCommand

class MacroBonusGameComplete(MacroCommand):
    def _onValues(self, values):
        pass

    def _onInitialize(self):
        pass

    def _onGenerate(self, source):
        source.addTask("TaskFunction", Fn=Mengine.changeCurrentAccountSetting, Args=("IsBonusChapter", u"4"))
        source.addTask("TaskNotify", ID=Notificator.onBonusGameComplete)
        pass
    pass