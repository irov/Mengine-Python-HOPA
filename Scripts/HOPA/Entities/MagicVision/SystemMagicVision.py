from Foundation.DemonManager import DemonManager
from Foundation.GuardBlockInput import GuardBlockInput
from Foundation.System import System
from Foundation.TaskManager import TaskManager
from HOPA.TransitionManager import TransitionManager

from MagicVisionManager import MagicVisionManager

class SystemMagicVision(System):
    def __init__(self):
        super(SystemMagicVision, self).__init__()
        pass

    def _onRun(self):
        self.onMagicVisionDoneObserver = Notification.addObserver(Notificator.onMagicVisionDone, self.__onMagicVisionDone)
        self.onMagicVisionStartObserver = Notification.addObserver(Notificator.onMagicVisionStart, self.__onMagicVisionStart)
        self.onMagicVisionBlockObserver = Notification.addObserver(Notificator.onMagicVisionBlockScene, self.__onBlockScene)
        self.onMagicVisionUnblockObserver = Notification.addObserver(Notificator.onMagicVisionUnblockScene, self.__onUnblockScene)
        self.MagicVision = DemonManager.getDemon("MagicVision")
        pass

    def __onBlockScene(self, sceneName):
        self.MagicVision.appendParam("BlockedScenes", sceneName)
        return False
        pass

    def __onUnblockScene(self, sceneName):
        self.MagicVision.delParam("BlockedScenes", sceneName)
        return False
        pass

    def __onMagicVisionDone(self, sceneName):
        sceneNameTo = MagicVisionManager.getSceneNameFrom(sceneName)
        self.MagicVision.appendParam("AllDoneScenes", sceneName)
        movieTransition = MagicVisionManager.getDeactivateMovie(sceneName)
        if movieTransition is None:
            TransitionManager.changeScene(sceneNameTo, None, False)
            return False
            pass

        if TaskManager.existTaskChain("MagicVisionAllDone") is True:
            TaskManager.cancelTaskChain("MagicVisionAllDone")
            pass

        with TaskManager.createTaskChain(Name="MagicVisionAllDone") as tc:
            with GuardBlockInput(tc) as guard_tc:
                guard_tc.addEnable(movieTransition)
                guard_tc.addTask("TaskMoviePlay", Movie=movieTransition, Wait=True)
                guard_tc.addDisable(movieTransition)
                pass

            tc.addFunction(TransitionManager.changeScene, sceneNameTo, None, False)
            pass

        return False
        pass

    def __onMagicVisionStart(self):
        self.MagicVision.setParam("State", "preActivate")
        return False
        pass

    def _onStop(self):
        Notification.removeObserver(self.onMagicVisionDoneObserver)
        Notification.removeObserver(self.onMagicVisionStartObserver)
        pass

    pass
