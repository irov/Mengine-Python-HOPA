from Foundation.SceneManager import SceneManager
from HOPA.Macro.MacroCommand import MacroCommand

class MacroZoomOpen(MacroCommand):
    def _onValues(self, values):
        self.ZoomName = values[0]
        pass

    def _onInitialize(self):
        if _DEVELOPMENT is True:
            if SceneManager.hasSceneZoom(self.SceneName, self.ZoomName) is False:
                self.initializeFailed("Scene '%s' not found zoom '%s'" % (self.SceneName, self.ZoomName))
                pass
            pass
        pass

    def _onGenerate(self, source):
        source.addTask("TaskZoomOpen", ZoomName=self.ZoomName, SceneName=self.SceneName)
        pass
    pass