from Foundation.DemonManager import DemonManager
from HOPA.Macro.MacroCommand import MacroCommand


class MacroMagicVisionStart(MacroCommand):
    def _onValues(self, values):
        pass

    def _onInitialize(self):
        if _DEVELOPMENT is True:
            MagicVision = DemonManager.getDemon("MagicVision")

            if MagicVision is None:
                self.initializeFailed("MacroMagicVisionDone not found MagicVision -> incorrect using of macro")
                pass
            pass
        pass

    def _onGenerate(self, source):
        source.addNotify(Notificator.onMagicVisionStart)
        pass

    pass
