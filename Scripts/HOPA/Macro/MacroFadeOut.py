from HOPA.Macro.MacroCommand import MacroCommand

class MacroFadeOut(MacroCommand):
    def _onValues(self, values):
        if len(values) != 0:
            self.FadeType = values[0]
            pass
        else:
            self.FadeType = None
            pass
        pass

    def _onGenerate(self, source):
        if self.FadeType is None:
            source.addTask("AliasFadeOut", FadeGroupName="Fade")
        elif self.FadeType == "Dialog":
            source.addTask("AliasFadeOut", FadeGroupName="FadeDialog")
            pass
        pass
    pass