from Foundation.Task.Task import Task
from Notification import Notification

class TaskQuestRun(Task):
    Skiped = False

    def _onParams(self, params):
        super(TaskQuestRun, self)._onParams(params)

        self.Quest = params.get("Quest")
        pass

    def _onInitialize(self):
        super(TaskQuestRun, self)._onInitialize()

        if _DEVELOPMENT is True:
            if self.Quest is None:
                self.initializeFailed("Quest is None")
                pass
            pass
        pass

    def _onRun(self):
        Notification.notify(Notificator.onQuestRun, self.Quest)

        return False
        pass

    def _onSkip(self):
        Notification.notify(Notificator.onQuestEnd, self.Quest)
        pass
    pass