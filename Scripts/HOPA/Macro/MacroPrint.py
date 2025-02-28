from HOPA.Macro.MacroCommand import MacroCommand


class MacroPrint(MacroCommand):
    def _onValues(self, values):
        self.Text = values[0]
        pass

    def _onInitialize(self):
        pass

    def _onGenerate(self, source):
        source.addPrint("MacroPrint: %s" % (self.Text))
        pass

    pass
