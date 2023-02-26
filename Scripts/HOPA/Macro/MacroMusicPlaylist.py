from HOPA.Macro.MacroCommand import MacroCommand

class MacroMusicPlaylist(MacroCommand):
    def _onValues(self, values):
        self.MusicPlaylistID = values[0]
        pass

    def _onGenerate(self, source):
        source.addNotify(Notificator.onMusicPlatlistPlay, self.MusicPlaylistID)
        # source.addPrint("   ".format(self.MusicPlaylistID))
        pass
    pass