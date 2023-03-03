from Foundation.Task.Task import Task
from Notification import Notification


class TaskMacroCommandRun(Task):
    Skiped = True

    def __init__(self):
        super(TaskMacroCommandRun, self).__init__()

    def _onParams(self, params):
        super(TaskMacroCommandRun, self)._onParams(params)

        self.ID = params.get("ID")
        self.CommandType = params.get("CommandType")
        self.SceneName = params.get("SceneName")
        self.GroupName = params.get("GroupName")

    def _onRun(self):
        Notification.notify(Notificator.onMacroCommandRun, self.ID, self.CommandType, self.SceneName, self.GroupName)

        return False

    def _onSkip(self):
        Notification.notify(Notificator.onMacroCommandEnd, self.ID, self.CommandType, self.SceneName, self.GroupName)
