from HOPA.Macro.MacroCommand import MacroCommand


class MacroBonusGameComplete(MacroCommand):
    def _onValues(self, values):
        pass

    def _onInitialize(self):
        pass

    def _onGenerate(self, source):
        source.addFunction(Mengine.changeCurrentAccountSetting, "IsBonusChapter", u"4")
        source.addNotify(Notificator.onBonusGameComplete)
        pass

    pass
