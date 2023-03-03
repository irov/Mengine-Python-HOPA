from Foundation.Task.MixinObserver import MixinObserver
from Foundation.Task.Task import Task
from HOPA.StageManager import StageManager


class TaskStageInit(MixinObserver, Task):
    Skiped = False

    def _onParams(self, params):
        super(TaskStageInit, self)._onParams(params)

        self.StageName = params.get("StageName", None)
        pass

    def _onInitialize(self):
        super(TaskStageInit, self)._onInitialize()
        #
        #        if StageManager.hasStage(self.StageName) is False:
        #            self.initializeFailed("Stage %s not found"%(self.StageName))
        #            pass
        pass

    def _onCheck(self):
        Stage = StageManager.getCurrentStage()
        if Stage is None:
            return True
            pass

        if self.StageName is None:
            return False
            pass

        if Stage.getName() == self.StageName:
            return False
            pass

        return True
        pass

    def _onRun(self):
        self.addObserver(Notificator.onStageInit, self._onStageFilter)

        return False
        pass

    def _onStageFilter(self, stageName):
        if self.StageName is None:
            return True
            pass

        if self.StageName != stageName:
            return False
            pass

        return True
        pass

    pass
