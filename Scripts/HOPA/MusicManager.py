from Foundation.DatabaseManager import DatabaseManager
from Foundation.DefaultManager import DefaultManager
from Foundation.Manager import Manager

class MusicManager(Manager):
    s_scenes = {}
    s_tags = {}
    s_default = None

    s_music_playlists = {}

    s_gameMusicResourceName = None
    s_menuMusicResourceName = None

    @staticmethod
    def _onInitialize():
        Manager.addObserver(Notificator.onChangeGameMusic, MusicManager.__onChangeGameMusic)
        Manager.addObserver(Notificator.onChangeMenuMusic, MusicManager.__onChangeMenuMusic)
        pass

    @staticmethod
    def __onChangeGameMusic(MusicResourceName):
        MusicManager.s_gameMusicResourceName = MusicResourceName

        return False
        pass

    @staticmethod
    def __onChangeMenuMusic(MusicResourceName):
        MusicManager.s_menuMusicResourceName = MusicResourceName

        return False
        pass

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        if param == 'Music':
            for record in records:
                SceneName = record.get("SceneName")
                PlaylistResourceName = record.get("PlaylistResourceName", None)

                MusicManager.s_scenes[SceneName] = PlaylistResourceName

        elif param == 'MusicPlaylists':
            for record in records:
                PlaylistID = record.get("PlaylistID")
                TrackID = record.get("TrackID")
                ResourceSoundName = record.get("ResourceSoundName")

                MusicManager.s_music_playlists[PlaylistID] = MusicManager.s_music_playlists.get(PlaylistID, [])
                MusicManager.s_music_playlists[PlaylistID].append((TrackID, ResourceSoundName))

        return True
        pass

    @staticmethod
    def getGameMusicResourceName():
        if MusicManager.s_gameMusicResourceName is None:
            MusicGameScene = DefaultManager.getDefault("MusicGameScene", None)

            MusicManager.s_gameMusicResourceName = MusicGameScene
            pass

        return MusicManager.s_gameMusicResourceName
        pass

    @staticmethod
    def getMenuMusicResourceName():
        if MusicManager.s_menuMusicResourceName is None:
            MusicMenuScene = DefaultManager.getDefault("MusicMenuScene", None)

            MusicManager.s_menuMusicResourceName = MusicMenuScene
            pass

        return MusicManager.s_menuMusicResourceName
        pass

    @staticmethod
    def getScenePlayList(sceneName):
        return MusicManager.s_scenes[sceneName]
        pass

    @staticmethod
    def hasScenePlayList(sceneName):
        return sceneName in MusicManager.s_scenes
        pass

    @staticmethod
    def getMusic():
        return MusicManager.s_scenes
        pass

    @staticmethod
    def getTags():
        return MusicManager.s_tags
        pass

    @staticmethod
    def getDefaultPlayList():
        return DefaultManager.getDefault("DefaultMusic")
        pass

    # - Playlists -------------------------------------------------------------------------------------
    @staticmethod
    def getMusicPlaylists():
        return MusicManager.s_music_playlists
    # -------------------------------------------------------------------------------------------------

    pass