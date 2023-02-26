from Foundation.Task.Task import Task

from HOPA.ScenarioManager import ScenarioManager

class TaskScenarioRun(Task):
    Skiped = True

    def _onParams(self, params):
        super(TaskScenarioRun, self)._onParams(params)

        self.ScenarioID = params.get("ScenarioID")
        pass

    def _onRun(self):
        ScenarioManager.runScenario(self.ScenarioID)

        return True
        pass
    pass