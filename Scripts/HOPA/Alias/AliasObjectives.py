from Foundation.Task.TaskAlias import TaskAlias
from Notification import Notification

class AliasObjectives(TaskAlias):
    def _onParams(self, params):
        super(AliasObjectives, self)._onParams(params)
        self.ObjectiveID = params.get("ObjectiveID")
        self.Notifies = params.get("Notifies")
        pass

    def _onGenerate(self, source):
        Notification.notify(Notificator.onObjectiveActivate, self.ObjectiveID, self.Notifies)
        pass