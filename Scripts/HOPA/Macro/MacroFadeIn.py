from HOPA.Macro.MacroCommand import MacroCommand


class MacroFadeIn(MacroCommand):
    def _onValues(self, values):
        if len(values) != 0:
            self.FadeType = values[0]
        else:
            self.FadeType = None

    def _onGenerate(self, source):
        if self.FadeType is None:
            source.addTask("AliasFadeIn", FadeGroupName="Fade")
        elif self.FadeType == "Dialog":
            source.addTask("AliasFadeIn", FadeGroupName="FadeDialog")
