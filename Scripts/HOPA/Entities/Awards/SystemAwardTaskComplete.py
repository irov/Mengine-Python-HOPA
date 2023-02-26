from Foundation.System import System
from Notification import Notification

from AwardsManager import AwardsManager

class SystemAwardTaskComplete(System):
    def _onParams(self, params):
        super(SystemAwardTaskComplete, self)._onParams(params)
        self.completedTasks = []
        pass

    def _onSave(self):
        return self.completedTasks
        pass

    def _onLoad(self, data_save):
        self.completedTasks = data_save
        pass

    def _onRun(self):
        self.addObserver(Notificator.onTasksClose, self.__onTasksClose)

        return True
        pass

    def _onStop(self):
        pass

    def __onTasksClose(self, taskID):
        if taskID in self.completedTasks:
            return False
            pass

        awardsId = AwardsManager.getTasksCompleteAwardID(taskID)
        if awardsId is None:
            return False
            pass

        else:
            self.completedTasks.append(taskID)
            Notification.notify(Notificator.onAwardsOpen, awardsId)
            pass
        return False
        pass

    pass