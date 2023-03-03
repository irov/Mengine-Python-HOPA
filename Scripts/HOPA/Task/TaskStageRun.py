from Foundation.Task.Task import Task

from HOPA.StageManager import StageManager


class TaskStageRun(Task):
    Skiped = True

    def _onParams(self, params):
        super(TaskStageRun, self)._onParams(params)

        self.StageName = params.get("StageName")
        pass

    def _onRun(self):
        if StageManager.runStage(self.StageName) is False:
            self.invalidTask("TaskStageRun invalid run Stage %s" % (self.StageName))
            pass

        return True
        pass

    pass
