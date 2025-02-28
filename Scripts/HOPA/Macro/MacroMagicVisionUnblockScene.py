from Foundation.DemonManager import DemonManager
from Foundation.SceneManager import SceneManager
from HOPA.Macro.MacroCommand import MacroCommand


class MacroMagicVisionUnblockScene(MacroCommand):
    def _onValues(self, values):
        self.SceneName = values[0]
        pass

    def _onInitialize(self):
        if _DEVELOPMENT is True:
            MagicVision = DemonManager.getDemon("MagicVision")

            if MagicVision is None:
                self.initializeFailed("MacroMagicVisionUnblockScene not found MagicVision -> incorrect using of macro")
                pass

            if SceneManager.hasScene(self.SceneName) is False:
                self.initializeFailed("MacroMagicVisionUnblockScene --- SceneName is not registered-> incorrect using of macro")
                pass
            pass
        pass

    def _onGenerate(self, source):
        source.addNotify(Notificator.onMagicVisionUnblockScene, self.SceneName)
        pass

    pass
