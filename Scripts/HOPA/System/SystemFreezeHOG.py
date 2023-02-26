# coding=utf-8
from Foundation.GroupManager import GroupManager
from Foundation.SceneManager import SceneManager
from Foundation.System import System
from HOPA.SemaphoreManager import SemaphoreManager

class SystemFreezeHOG(System):
    def _onParams(self, _params):
        self.semaphore = Semaphore("False", "SkipFreezeHOGCounter")
        SemaphoreManager.addSemaphore(self.semaphore)

    def _onRun(self):
        self.addObserver(Notificator.onTransitionClick, self.__cbClearFailCounter)
        self.addObserver(Notificator.onMacroClick, self.__cbClearFailCounter)
        self.addObserver(Notificator.onItemClick, self.__cbClearFailCounter)
        self.addObserver(Notificator.onMovieSocketClick, self.__cbClearFailCounter)
        self.addObserver(Notificator.onMovie2ButtonClick, self.__cbClearFailCounter)
        self.addObserver(Notificator.onSocketClick, self.__cbSocketClick)
        self.addObserver(Notificator.onNodeSocketClickSuccessful, self.__cbSocketClick)

        return True

    def __cbSocketClick(self, socket, *args):
        current_scene_name = SceneManager.getCurrentSceneName()

        if GroupManager.hasObject(current_scene_name, "Socket_SocketFreeze"):
            if socket == GroupManager.getObject(current_scene_name, "Socket_SocketFreeze"):
                return False

        if GroupManager.hasObject("BlockInput", "Socket_Click"):
            if socket == GroupManager.getObject("BlockInput", "Socket_Click"):
                return False

        self.semaphore.setValue(True)
        return False

    def __cbClearFailCounter(self, *args):
        self.semaphore.setValue(True)
        return False