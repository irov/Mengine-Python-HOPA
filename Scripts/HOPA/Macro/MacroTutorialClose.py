from HOPA.Macro.MacroCommand import MacroCommand


class MacroTutorialClose(MacroCommand):
    def _onGenerate(self, source):
        source.addNotify(Notificator.onTutorialHide)
        pass
