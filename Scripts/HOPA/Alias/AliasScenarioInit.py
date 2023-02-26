from Foundation.Task.TaskAlias import TaskAlias

class AliasScenarioInit(TaskAlias):
    def _onParams(self, params):
        super(AliasScenarioInit, self)._onParams(params)
        self.ScenarioRunner = params.get("ScenarioRunner")
        pass

    def _onGenerate(self, source):
        if self.ScenarioRunner.isPlusScene is True:
            source.addTask("TaskScenePlusInit", SceneName=self.ScenarioRunner.SceneName)
            pass
        elif self.ScenarioRunner.isZoom is True:
            source.addTask("TaskZoomInit", SceneName=self.ScenarioRunner.SceneName, ZoomName=self.ScenarioRunner.GroupName)
            pass
        else:
            source.addTask("TaskSceneInit", SceneName=self.ScenarioRunner.SceneName)
        pass
    pass