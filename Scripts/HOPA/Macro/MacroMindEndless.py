from HOPA.Macro.MacroCommand import MacroCommand

class MacroMindEndless(MacroCommand):
    def _onValues(self, values):
        pass

    def _onInitialize(self):
        pass

    def _onGenerate(self, source):
        source.addNotify(Notificator.onGroupEnableMacro, self.GroupName)
        pass
    pass