from Foundation.DemonManager import DemonManager
from Foundation.SceneManager import SceneManager
from HOPA.Macro.MacroCommand import MacroCommand


class MacroMagicVisionBlockScene(MacroCommand):
    def _onValues(self, values):
        self.SceneName = values[0]

    def _onInitialize(self):
        if _DEVELOPMENT is True:
            MagicVision = DemonManager.getDemon("MagicVision")

            if MagicVision is None:
                self.initializeFailed("MacroMagicVisionBlockScene not found MagicVision -> incorrect using of macro")

            if SceneManager.hasScene(self.SceneName) is False:
                self.initializeFailed("MacroMagicVisionBlockScene --- SceneName is not registered-> incorrect using of macro")

    def _onGenerate(self, source):
        source.addTask("TaskNotify", ID=Notificator.onMagicVisionBlockScene, Args=(self.SceneName,))

