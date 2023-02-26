from Foundation.GroupManager import GroupManager
from Foundation.System import System
from Foundation.TaskManager import TaskManager
from Notification import Notification

class SystemTutorialSkip(System):
    def __init__(self):
        super(SystemTutorialSkip, self).__init__()

        self.progress = {}
        self.final = False
        self.isTutorialStart = False
        self.button = None

    def _onRun(self):
        self.__setObservers()

        return True

    def __setObservers(self):
        self.addObserver(Notificator.onTutorial_Start, self.__cbTutorialStart)
        self.addObserver(Notificator.onTutorialProgres, self.__cbTutorialProgres)

    def __cbTutorialStart(self):
        self._runTaskChain()
        return False

    def __cbTutorialProgres(self, progress_name, progress_action, progress_group):
        if progress_name in self.progress:
            self.progress.pop(progress_name)
            return False

        self.progress[progress_name] = (progress_action, progress_group)
        return False

    def _tutorialUnblock(self, spike=""):
        self.button.returnToParent()

        for key in self.progress:
            if GroupManager.hasObject(self.progress[key][1] + spike, key) is False:
                if self.progress[key][0] is "ZoomBlockClose":
                    Notification.notify(Notificator.onZoomBlockClose, key, False)
                continue

            obj = GroupManager.getObject(self.progress[key][1] + spike, key)

            if self.progress[key][0] == "Enable":
                obj.setEnable(False)
            elif self.progress[key][0] == "Disable":
                obj.setEnable(True)

    def _tutorialSkip(self):
        if self.isTutorialStart is False:
            return False

        self._tutorialUnblock()
        self._tutorialUnblock("_Over")

        Notification.notify(Notificator.onTutorialSkipEnd)

        self.progress = {}
        self._tcCancel()

        return False

    def _runTaskChain(self):
        self.button = GroupManager.getObject("SkipTutorial", "Movie2Button_Skip")

        with TaskManager.createTaskChain(Name="SystemTutorialSkip", GroupName="SkipTutorial") as tc:
            tc.addFunction(self._started)

            tc.addTask("TaskEnable", ObjectName="Movie2Button_Skip", Value=True)
            tc.addTask("TaskMovie2ButtonClick", Movie2Button=self.button)
            tc.addFunction(self._tutorialSkip)

    def _started(self):
        self.isTutorialStart = True

    def _onStop(self):
        self._tcCancel()

    def _tcCancel(self):
        if TaskManager.existTaskChain("SystemTutorialSkip") is True:
            TaskManager.cancelTaskChain("SystemTutorialSkip")

    def _onSave(self):
        data_save = (self.progress, self.final, self.isTutorialStart)
        return data_save

    def _onLoad(self, data_save):
        if data_save is None:
            return

        self.progress, self.final, self.isTutorialStart = data_save

        if self.progress == {}:
            return

        if self.isTutorialStart:
            self._runTaskChain()