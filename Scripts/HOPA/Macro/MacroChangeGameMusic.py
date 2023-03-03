from HOPA.Macro.MacroCommand import MacroCommand


class MacroChangeGameMusic(MacroCommand):
    def _onValues(self, values):
        self.MusicResourceName = values[0]
        pass

    def _onGenerate(self, source):
        source.addNotify(Notificator.onChangeGameMusic, self.MusicResourceName)
        pass

    pass
