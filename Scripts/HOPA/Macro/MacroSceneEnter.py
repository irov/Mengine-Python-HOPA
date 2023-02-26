from HOPA.Macro.MacroCommand import MacroCommand

class MacroSceneEnter(MacroCommand):
    def _onGenerate(self, source):
        if self.ScenarioRunner.isZoom is True:
            source.addTask("TaskZoomEnter", ZoomName=self.GroupName, SceneName=self.SceneName, isEnter=False)
            pass
        else:
            source.addTask("TaskSceneEnter", SceneName=self.SceneName, isEnter=False)
            pass
        pass
    pass