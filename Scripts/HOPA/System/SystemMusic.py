from Foundation.SceneManager import SceneManager
from Foundation.System import System
from HOPA.MusicManager import MusicManager
from HOPA.ScenarioManager import ScenarioManager

class SystemMusic(System):
    def __init__(self):
        super(SystemMusic, self).__init__()

        self.PlayList = None

        self.onSceneInitObserver = None
        self.onMusicPlayObserver = None
        self.playMusic = False
        self.pauseMusic = False
        self.easing = "easyLinear"

        self.playLists = {}
        pass

    def _onInitialize(self):
        super(SystemMusic, self)._onInitialize()

        pass

    def _onRun(self):
        self.addObserver(Notificator.onSceneInit, self.__onSceneInit)
        self.addObserver(Notificator.onMusicPlay, self.__onMusicPlay)

        return True
        pass

    def onPlayMusic(self):
        self.__onMusicPlay("temp")
        pass

    def __onMusicPlay(self, name):
        currentSceneName = SceneManager.getCurrentSceneName()
        self.__onSceneInit(currentSceneName)
        return False
        pass

    def _onStop(self):
        self.stopMusic()
        pass

    def _isPlusScene(self, sceneName):
        scenarioID = ScenarioManager.getScenarioIdBySceneName(sceneName)

        if scenarioID is None:
            return False

        scenario = ScenarioManager.getScenario(scenarioID)

        if scenario is None:
            return False

        if scenario.PlusName is not None:
            return True

        return False

    def __onSceneInit(self, sceneName):
        if self._isPlusScene(sceneName) is True:
            # print " <SystemMusic> __onSceneInit scene {} is PlusScene".format(sceneName)
            return False

        hasScenePlayList = MusicManager.hasScenePlayList(sceneName)
        if hasScenePlayList is False:
            currentPlayList = MusicManager.getDefaultPlayList()
            pass
        else:
            currentPlayList = MusicManager.getScenePlayList(sceneName)
            pass

        # print " <SystemMusic> __onSceneInit", sceneName, hasScenePlayList, currentPlayList

        if currentPlayList is None:
            if self.playMusic is True:
                self.__musicPause()
                self.pauseMusic = True
                pass
            return False
            pass

        elif self.playMusic is True:
            if currentPlayList == self.PlayList and self.pauseMusic == True:
                Mengine.musicResume()
                self.pauseMusic = False
                return False
                pass
            elif currentPlayList != self.PlayList:
                self.__playNext(currentPlayList)
                self.playMusic = True
                return False
                pass
            else:
                return False
                pass
            pass
        if self.playMusic is False:
            if currentPlayList in self.playLists.keys():
                pos, index = self.playLists[currentPlayList]
                Mengine.musicFadeOut(currentPlayList, pos, True, 250.0, self.easing, None)
                # Mengine.musicPlayTrack(currentPlayList, index, pos, True)
                pass
            else:
                self.__playNext(currentPlayList)
                pass

            self.PlayList = currentPlayList
            self.playMusic = True
            pass

        return False
        pass

    def __musicPause(self):
        Mengine.musicPause()
        pass

    def __playNext(self, currentPlayList):
        # if self.PlayList is not None:
        #     pos = Mengine.musicGetPosMs()
        #     index = Mengine.musicGetPlayingTrackIndex()
        #     self.playLists[self.PlayList] = (pos, index)
        #     # Mengine.musicStop()
        #     Mengine.musicFadeIn(250.0, None)
        #     pass

        if self.PlayList is not None:
            Mengine.musicFadeIn(250.0, self.easing, None)
            pass

        if currentPlayList in self.playLists.keys():
            pos, index = self.playLists[currentPlayList]

            Mengine.musicFadeOut(currentPlayList, pos, True, 250.0, self.easing, None)
            # Mengine.musicPlayTrack(currentPlayList, index, pos, True)

            pass
        else:
            Mengine.musicFadeOut(currentPlayList, 0, True, 250.0, self.easing, None)
            # Mengine.musicPlayTrack(currentPlayList, 0, 0, True)

            pass

        self.PlayList = currentPlayList
        pass

    def stopMusic(self):
        Mengine.musicStop()
        self.playMusic = False
        pass

    pass