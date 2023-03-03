from HOPA.Macro.MacroCommand import MacroCommand


class MacroTransitionBlock(MacroCommand):
    def _onGenerate(self, source):
        source.addTask("TaskTransitionBlock", Value=True, IsGameScene=True)
        pass

    pass
