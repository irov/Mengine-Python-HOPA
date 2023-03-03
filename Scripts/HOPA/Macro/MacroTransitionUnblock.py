from HOPA.Macro.MacroCommand import MacroCommand


class MacroTransitionUnblock(MacroCommand):
    def _onGenerate(self, source):
        source.addTask("TaskTransitionBlock", Value=False, IsGameScene=True)
        pass

    pass
