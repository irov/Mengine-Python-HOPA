from HOPA.Macro.MacroCommand import MacroCommand


class MacroMusicFadeOut(MacroCommand):
    def _onValues(self, values):
        self.FadeTime = float(values[0])
        pass

    def _onInitialize(self, **params):
        if _DEVELOPMENT is True:
            if self.FadeTime is None:
                self.initializeFailed("MacroMusicFadeOut ->FadeTime is not define!!! %s" % (self.FadeTime))
                pass
            pass
        pass

    def _onGenerate(self, source):
        source.addTask("TaskMusicFadeOut", FadeTime=self.FadeTime)
        pass

    pass
