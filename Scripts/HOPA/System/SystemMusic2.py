from Foundation.DatabaseManager import DatabaseManager
from Foundation.DefaultManager import DefaultManager
from Foundation.SceneManager import SceneManager
from Foundation.System import System


class SystemMusic2(System):
    class MusicDesc(object):
        def __init__(self):
            self.play = False
            self.pos = 0.0
            pass

        pass

    def __init__(self):
        super(SystemMusic2, self).__init__()

        self.EventMusicPlay = False
        self.EventMusicPlaySchedulerId = 0

        self.EventGlobalMusicPlay = False

        self.ORM_Music = None

        self.musics = {}

        self.MusicGameScene = None
        self.MusicMenuScene = None
        self.easing = "easyLinear"

        # self.MusicFadeInTime = DefaultManager.getDefaultFloat("MusicFadeInTime", 1)
        # self.MusicFadeInTime *= 1000  # speed fix
        # self.MusicFadeOutTime = DefaultManager.getDefaultFloat("MusicFadeOutTime", 1)
        # self.MusicFadeOutTime *= 1000  # speed fix
        pass

    def _onInitialize(self):
        super(SystemMusic2, self)._onInitialize()

        self.ORM_Music = DatabaseManager.getDatabaseORMs("Database", "Music")
        pass

    def _onRun(self):
        self.addObserver(Notificator.onTransitionBegin, self.__onTransitionBegin)
        self.addObserver(Notificator.onTransitionEnd, self.__onTransitionEnd)
        self.addObserver(Notificator.onMusicPlay, self.__onMusicPlay)

        self.addObserver(Notificator.onChangeGameMusic, self.__onChangeGameMusic)
        self.addObserver(Notificator.onChangeMenuMusic, self.__onChangeMenuMusic)

        self.MusicGameScene = DefaultManager.getDefault("MusicGameScene", None)
        self.MusicMenuScene = DefaultManager.getDefault("MusicMenuScene", None)

        return True
        pass

    def _onStop(self):
        Mengine.musicStop()

        self.musics = {}

        if self.EventMusicPlaySchedulerId != 0:
            Mengine.scheduleGlobalRemove(self.EventMusicPlaySchedulerId)
            self.EventMusicPlaySchedulerId = 0
            pass
        pass

    def __findRemoveMusicResourceName(self, sceneFrom, sceneTo):
        ORM_OldMusic = DatabaseManager.find(self.ORM_Music, SceneName=sceneFrom)
        ORM_NewMusic = DatabaseManager.find(self.ORM_Music, SceneName=sceneTo)

        if ORM_OldMusic is not None:
            if ORM_NewMusic is not None and ORM_NewMusic.Except is True:
                return None
                pass

            if ORM_OldMusic.PlaylistResourceName is None:
                return None
                pass

            if sceneTo is None:
                return ORM_OldMusic.PlaylistResourceName
                pass

            if ORM_NewMusic is not None:
                if ORM_OldMusic.PlaylistResourceName == ORM_NewMusic.PlaylistResourceName:
                    return None
                    pass
                pass

            return ORM_OldMusic.PlaylistResourceName
            pass

        if ORM_NewMusic is not None:
            if ORM_NewMusic.Except is True:
                return None
                pass

            if ORM_NewMusic.PlaylistResourceName is None:
                self.EventGlobalMusicPlay = False

                if sceneFrom is None:
                    return None
                    pass

                if SceneManager.isGameScene(sceneFrom) is True:
                    return self.MusicGameScene
                    pass

                return self.MusicMenuScene
                pass
            pass

        if SceneManager.isGameScene(sceneFrom) is True:
            if SceneManager.isGameScene(sceneTo) is True:
                return None
                pass

            self.EventGlobalMusicPlay = False

            return self.MusicGameScene
            pass

        if SceneManager.isGameScene(sceneTo) is False:
            return None
            pass

        self.EventGlobalMusicPlay = False

        return self.MusicMenuScene
        pass

    def __onTransitionBegin(self, sceneFrom, sceneTo, zoomName):
        if self.EventMusicPlay is True:
            return False
            pass

        MusicResource = self.__findRemoveMusicResourceName(sceneFrom, sceneTo)

        if MusicResource is None:
            return False
            pass

        if self.musics.get(MusicResource) is None:
            return False

        Desc = self.musics[MusicResource]
        PosMs = Mengine.musicGetPosMs()

        Desc.play = False
        Desc.pos = PosMs

        Mengine.musicFadeIn(250.0, self.easing, None)

        return False
        pass

    def __findNewMusicResourceName(self, sceneFrom, sceneTo):
        ORM_OldMusic = DatabaseManager.find(self.ORM_Music, SceneName=sceneFrom)

        if ORM_OldMusic is not None and ORM_OldMusic.Except is True:
            return None
            pass

        ORM_NewMusic = DatabaseManager.find(self.ORM_Music, SceneName=sceneTo)

        if ORM_NewMusic is not None:
            if ORM_NewMusic.Except is True:
                return None
                pass

            self.EventGlobalMusicPlay = False

            if ORM_NewMusic.PlaylistResourceName is None:
                return None
                pass

            if sceneFrom is None:
                return ORM_NewMusic.PlaylistResourceName
                pass

            if ORM_OldMusic is not None:
                if ORM_OldMusic.PlaylistResourceName == ORM_NewMusic.PlaylistResourceName:
                    return None
                    pass
                pass

            return ORM_NewMusic.PlaylistResourceName
            pass

        if SceneManager.isGameScene(sceneTo) is True:
            if SceneManager.isGameScene(sceneFrom) is True and self.EventGlobalMusicPlay is True:
                return None
                pass

            self.EventGlobalMusicPlay = True

            return self.MusicGameScene
            pass

        if SceneManager.isGameScene(sceneTo) is False and self.EventGlobalMusicPlay is True:
            return None
            pass

        self.EventGlobalMusicPlay = True

        return self.MusicMenuScene
        pass

    def __onTransitionEnd(self, sceneFrom, sceneTo, zoomName):
        if self.EventMusicPlay is True:
            return False
            pass

        MusicResource = self.__findNewMusicResourceName(sceneFrom, sceneTo)

        if MusicResource is None:
            return False
            pass

        # print "__onTransitionEnd", MusicResource, self.EventGlobalMusicPlay

        Desc = self.musics.setdefault(MusicResource, SystemMusic2.MusicDesc())

        Desc.play = True

        Mengine.musicFadeOut(MusicResource, Desc.pos, True, 1000.0, self.easing, None)

        return False
        pass

    def __onMusicPlay(self, MusicResource):
        if self.EventMusicPlay is True:
            return False
            pass

        CurrentSceneName = SceneManager.getCurrentSceneName()

        self.__onTransitionBegin(None, CurrentSceneName, None)

        self.EventMusicPlay = True

        Mengine.musicFadeOut(MusicResource, 0.0, False, 1000.0, self.easing, None)

        duration = Mengine.musicGetLengthMs()

        self.EventMusicPlaySchedulerId = Mengine.scheduleGlobal(duration, self.__endMusicPlay)

        return False
        pass

    def __endMusicPlay(self, id, isRemoved):
        self.EventMusicPlay = False
        self.EventMusicPlaySchedulerId = 0

        Mengine.musicStop()

        CurrentSceneName = SceneManager.getCurrentSceneName()

        self.__onTransitionEnd(None, CurrentSceneName, None)
        pass

    def __onChangeGameMusic(self, MusicResourceName):
        if self.MusicGameScene == MusicResourceName:
            return False
            pass

        self.MusicGameScene = MusicResourceName

        # print "__onChangeGameMusic", self.MusicGameScene

        if self.EventMusicPlay is True:
            return False
            pass

        if SceneManager.isCurrentGameScene() is False:
            return False
            pass

        Mengine.musicStop()

        Desc = self.musics.setdefault(MusicResourceName, SystemMusic2.MusicDesc())

        Desc.play = True

        Mengine.musicFadeOut(MusicResourceName, Desc.pos, True, 1000.0, self.easing, None)

        return False
        pass

    def __onChangeMenuMusic(self, MusicResourceName):
        if self.MusicMenuScene == MusicResourceName:
            return False
            pass

        self.MusicMenuScene = MusicResourceName

        if self.EventMusicPlay is True:
            return False
            pass

        if SceneManager.isCurrentGameScene() is True:
            return False
            pass

        Mengine.musicStop()

        Desc = self.musics.setdefault(MusicResourceName, SystemMusic2.MusicDesc())

        Desc.play = True

        Mengine.musicFadeOut(MusicResourceName, Desc.pos, True, 1000.0, self.easing, None)

        return False
        pass

    pass
