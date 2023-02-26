from Foundation.Task.MixinObserver import MixinObserver
from Foundation.Task.Task import Task

class TaskScenarioEnd(MixinObserver, Task):
    #    Skiped = False
    Skiped = True

    def _onParams(self, params):
        super(TaskScenarioEnd, self)._onParams(params)

        self.ScenarioID = params.get("ScenarioID")
        pass

    def _onRun(self):
        def __onScenarioEndFilter(scenarioID):
            return True
            pass

        self.addObserverFilter(Notificator.onScenarioComplete, __onScenarioEndFilter, self.ScenarioID)

        return False
        pass
    pass