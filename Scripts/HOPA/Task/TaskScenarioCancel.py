from Foundation.Task.Task import Task

from HOPA.ScenarioManager import ScenarioManager


class TaskScenarioCancel(Task):
    Skiped = True

    def _onParams(self, params):
        super(TaskScenarioCancel, self)._onParams(params)

        self.ScenarioID = params.get("ScenarioID")

    def _onRun(self):
        ScenarioManager.cancelScenario(self.ScenarioID)

        return True
