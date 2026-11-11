from Foundation.Task.Task import Task
from HOPA.QuestManager import QuestManager
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

    def _onRun(self):
        Notification.notify(Notificator.onQuestRun, self.Quest)

        return False

    def _onSkip(self):
        Notification.notify(Notificator.onQuestEnd, self.Quest)
        pass

    def _onFinally(self):
        super(TaskQuestRun, self)._onFinally()

        QuestManager.cancelQuest(self.Quest)

    def _onFinalize(self):
        super(TaskQuestRun, self)._onFinalize()
        self.Quest = None