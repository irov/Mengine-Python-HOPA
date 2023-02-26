from HOPA.Macro.MacroCommand import MacroCommand

class MacroSceneInit(MacroCommand):
    def _onGenerate(self, source):
        if self.ScenarioRunner.isZoom is True:
            source.addTask("TaskZoomInit", SceneName=self.SceneName, ZoomName=self.GroupName)
            pass
        else:
            source.addTask("TaskSceneInit", SceneName=self.SceneName)
            pass
        pass
    pass