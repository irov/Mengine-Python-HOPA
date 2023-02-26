from Foundation.Task.MixinObserver import MixinObserver
from Foundation.Task.Task import Task
from HOPA.ScenarioManager import ScenarioManager

class TaskScenarioLeave(MixinObserver, Task):
    Skiped = False

    def _onParams(self, params):
        super(TaskScenarioLeave, self)._onParams(params)

        self.ScenarioId = params.get("ScenarioId")
        pass

    def _onInitialize(self):
        super(TaskScenarioLeave, self)._onInitialize()

        if _DEVELOPMENT is True:
            if ScenarioManager.hasScenario(self.ScenarioId) is False:
                self.initializeFailed("ScenarioId %s not found" % (self.ScenarioId))
                pass
            pass
        pass

    def _onCheck(self):
        if ScenarioManager.isScenarioEnter(self.ScenarioId) is False:
            return False
            pass

        return True
        pass

    def _onRun(self):
        self.addObserver(Notificator.onScenarioLeave, self._onScenarioIdFilter)
        return False
        pass

    def _onScenarioIdFilter(self, ScenarioId):
        if self.ScenarioId != ScenarioId:
            return False
            pass

        return True
        pass
    pass