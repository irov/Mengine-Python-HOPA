from HOPA.Macro.MacroCommand import MacroCommand


class MacroChangeMenuMusic(MacroCommand):
    def _onValues(self, values):
        self.MusicResourceName = values[0]
        pass

    def _onGenerate(self, source):
        source.addNotify(Notificator.onChangeMenuMusic, self.MusicResourceName)
        pass

    pass
