from Foundation.Task.TaskAlias import TaskAlias

class AliasObjectives(TaskAlias):
    def _onParams(self, params):
        super(AliasObjectives, self)._onParams(params)
        self.ObjectiveID = params.get("ObjectiveID")
        self.Notifies = params.get("Notifies")

    def _onGenerate(self, source):
        Notification.notify(Notificator.onObjectiveActivate, self.ObjectiveID, self.Notifies)
