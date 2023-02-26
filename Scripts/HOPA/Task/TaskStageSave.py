from Foundation.Task.Task import Task
from HOPA.StageManager import StageManager
from Notification import Notification

class TaskStageSave(Task):
    Skiped = True

    def _onParams(self, params):
        super(TaskStageSave, self)._onParams(params)
        pass

    def _onRun(self):
        Notification.notify(Notificator.onStageSave)

        StageManager.saveStage()
        return True
        pass

    pass