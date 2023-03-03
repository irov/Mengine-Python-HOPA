from Foundation.Task.MixinObserver import MixinObserver
from Foundation.Task.Task import Task
from HOPA.ScenarioManager import ScenarioManager


class TaskScenarioInit(MixinObserver, Task):
    Skiped = False

    def _onParams(self, params):
        super(TaskScenarioInit, self)._onParams(params)

        self.ScenarioId = params.get("ScenarioId")
        pass

    def _onInitialize(self):
        super(TaskScenarioInit, self)._onInitialize()

        if _DEVELOPMENT is True:
            if ScenarioManager.hasScenario(self.ScenarioId) is False:
                self.initializeFailed("ScenarioId %s not found" % (self.ScenarioId))
                pass
            pass
        pass

    def _onCheck(self):
        if ScenarioManager.isScenarioInit(self.ScenarioId) is True:
            return False
            pass

        return True
        pass

    def _onRun(self):
        self.addObserver(Notificator.onScenarioInit, self._onScenarioIdFilter)

        return False
        pass

    def _onScenarioIdFilter(self, ScenarioId):
        if self.ScenarioId != ScenarioId:
            return False
            pass

        return True
        pass

    pass
