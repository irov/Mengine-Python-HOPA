from HOPA.Macro.MacroCommand import MacroCommand


class MacroDeadLock(MacroCommand):
    def _onGenerate(self, source):
        source.addBlock()
        pass

    pass
