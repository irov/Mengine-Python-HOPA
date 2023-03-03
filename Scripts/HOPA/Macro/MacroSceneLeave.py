from HOPA.Macro.MacroCommand import MacroCommand


class MacroSceneLeave(MacroCommand):
    def _onGenerate(self, source):
        if self.ScenarioRunner.isZoom is True:
            source.addTask("TaskZoomLeave", ZoomName=self.GroupName, SceneName=self.SceneName)
            pass
        else:
            source.addTask("TaskSceneLeave", SceneName=self.SceneName)
            pass
        pass

    pass
