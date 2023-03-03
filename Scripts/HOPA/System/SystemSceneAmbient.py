from Foundation.System import System

from HOPA.AmbientManager import AmbientManager


class SystemSceneAmbient(System):
    def __init__(self):
        super(SystemSceneAmbient, self).__init__()
        self.onSceneInitObserver = None
        pass

    def _onInitialize(self):
        super(SystemSceneAmbient, self)._onInitialize()
        pass

    def _onRun(self):
        self.addObserver(Notificator.onSceneInit, self.__onSceneInit)

        return True
        pass

    def _onStop(self):
        pass

    def __onSceneInit(self, sceneName):
        if AmbientManager.hasAmbient(sceneName) is False:
            return False
            pass

        Demon_Switch, AmbientName = AmbientManager.getAmbient(sceneName)
        Demon_Switch.setSwitch(AmbientName)
        return False
        pass

    pass
