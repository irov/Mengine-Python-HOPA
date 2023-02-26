from Foundation.Task.TaskAlias import TaskAlias

class AliasScenarioEnter(TaskAlias):
    def _onParams(self, params):
        super(AliasScenarioEnter, self)._onParams(params)
        self.ScenarioRunner = params.get("ScenarioRunner")
        pass

    def _onGenerate(self, source):
        if self.ScenarioRunner.isPlusScene is True:
            source.addTask("TaskScenePlusEnter", SceneName=self.ScenarioRunner.SceneName)
            pass
        elif self.ScenarioRunner.isZoom is True:
            source.addTask("TaskZoomEnter", SceneName=self.ScenarioRunner.SceneName, ZoomName=self.ScenarioRunner.GroupName)
        else:
            source.addTask("TaskSceneEnter", SceneName=self.ScenarioRunner.SceneName)
            source.addTask("TaskZoomEmpty")
            pass
        pass

    pass