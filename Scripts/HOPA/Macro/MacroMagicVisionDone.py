from Foundation.DemonManager import DemonManager
from Foundation.SceneManager import SceneManager
from HOPA.Macro.MacroCommand import MacroCommand


class MacroMagicVisionDone(MacroCommand):
    def _onValues(self, values):
        pass

    def _onInitialize(self):
        if _DEVELOPMENT is True:
            MagicVision = DemonManager.getDemon("MagicVision")

            if MagicVision is None:
                self.initializeFailed("MacroMagicVisionDone not found MagicVision -> incorrect using of macro")

    def _onGenerate(self, source):
        def scope(scope):
            SceneName = SceneManager.getCurrentGameSceneName()
            scope.addTask("TaskNotify", ID=Notificator.onMagicVisionDone, Args=(SceneName,))

        source.addTask("TaskScope", Scope=scope)

