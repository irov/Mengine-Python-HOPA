from Foundation.Task.Task import Task

from HOPA.ScenarioManager import ScenarioManager


class TaskScenarioSkip(Task):
    Skiped = True

    def _onParams(self, params):
        super(TaskScenarioSkip, self)._onParams(params)

        self.ScenarioID = params.get("ScenarioID")
        pass

    def _onRun(self):
        ScenarioManager.skipScenario(self.ScenarioID)

        return True
        pass

    pass
