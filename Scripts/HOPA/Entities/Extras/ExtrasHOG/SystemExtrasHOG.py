from Foundation.System import System
from Foundation.TaskManager import TaskManager
from HOPA.ChapterManager import ChapterManager
from Notification import Notification


class SystemExtrasHOG(System):
    def __init__(self):
        super(SystemExtrasHOG, self).__init__()
        self.ExtraHOGPlayObserver = None
        pass

    def _onRun(self):
        self.ExtraHOGPlayObserver = Notification.addObserver(Notificator.onExtraHOGPlay, self._playExtraHOG)
        return True
        pass

    def _onStop(self):
        Notification.removeObserver(self.ExtraHOGPlayObserver)
        self.ExtraHOGPlayObserver = None

        if TaskManager.existTaskChain("ExtraHOGToolbar") is True:
            TaskManager.cancelTaskChain("ExtraHOGToolbar")
            pass
        pass

    def _playExtraHOG(self, sceneName, scenarioID):
        if TaskManager.existTaskChain("ExtraHOGToolbar") is True:
            TaskManager.cancelTaskChain("ExtraHOGToolbar")
            pass

        def ScenarioInjection(scenarioID):
            currentScenarioChapter = ChapterManager.getCurrentChapter()
            ChapterManager.chapterAddRunInjection(currentScenarioChapter, scenarioID)
            pass

        with TaskManager.createTaskChain() as tc:
            tc.addTask("AliasTransition", SceneName=sceneName)
            tc.addTask("TaskFunction", Fn=ScenarioInjection, Args=(scenarioID,))
            pass

        with TaskManager.createTaskChain(Name="ExtraHOGToolbar") as tc:
            tc.addTask("TaskButtonClick", GroupName="ExtraToolbar", ButtonName="Button_Menu", AutoEnable=True)
            tc.addTask("AliasTransition", SceneName="ExtrasHOG")
            pass
        pass

        return False
        pass

    pass
