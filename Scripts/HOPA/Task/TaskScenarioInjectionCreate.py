from Foundation.Task.Task import Task

from HOPA.ChapterManager import ChapterManager

class TaskScenarioInjectionCreate(Task):
    Skiped = False

    def _onParams(self, params):
        super(TaskScenarioInjectionCreate, self)._onParams(params)

        self.ScenarioID = params.get("ScenarioID")
        pass

    def _onRun(self):
        currentScenarioChapter = ChapterManager.getCurrentChapter()
        ChapterManager.chapterAddRunInjection(currentScenarioChapter, self.ScenarioID)
        return True
        pass
    pass