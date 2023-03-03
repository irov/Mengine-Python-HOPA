from HOPA.Macro.MacroCommand import MacroCommand


class MacroMusic(MacroCommand):
    def _onValues(self, values):
        self.MusicPlaylist = values[0]
        pass

    def _onGenerate(self, source):
        source.addNotify(Notificator.onMusicPlay, self.MusicPlaylist)
        pass

    pass
