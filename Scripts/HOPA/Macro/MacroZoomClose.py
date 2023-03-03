from HOPA.Macro.MacroCommand import MacroCommand


class MacroZoomClose(MacroCommand):
    #    def _onValues(self, values):
    #        self.ZoomName = values[0]
    #        pass

    #    def _onInitialize(self):
    #        if SceneManager.hasSceneZoom(self.GroupName, self.ZoomName) is False:
    #            self.initializeFailed("Zoom %s not found"%(self.ZoomName))
    #            pass
    #        pass

    def _onGenerate(self, source):
        source.addTask("TaskZoomClose", ZoomName=self.GroupName, SceneName=self.SceneName, Value=True)
        pass

    pass
