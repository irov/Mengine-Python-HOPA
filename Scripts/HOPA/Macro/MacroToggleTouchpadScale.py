from Foundation.SystemManager import SystemManager
from HOPA.EnigmaManager import EnigmaManager
from HOPA.Macro.MacroCommand import MacroCommand

class MacroToggleTouchpadScale(MacroCommand):

    def _onValues(self, values):
        self.block = not bool(values[0])
        self.enigma_name = values[1] if len(values) > 1 else None
        self.reset = True

    def _onInitialize(self):
        if _DEVELOPMENT is False:
            return

        if SystemManager.hasSystem("SystemCameraManipulation") is False:
            self.initializeFailed("system 'SystemCameraManipulation' not exists")

        if self.enigma_name is not None:
            if EnigmaManager.hasEnigma(self.enigma_name) is False:
                self.initializeFailed("enigma {!r} not found".format(self.enigma_name))

    def _toggle(self):
        SystemCameraManipulation = SystemManager.getSystem("SystemCameraManipulation")

        if self.enigma_name is None:
            # switch global block
            SystemCameraManipulation.setBlockHotspot(self.block, True)
        else:
            # switch block for enigma
            SystemCameraManipulation.setEnigmaBlock(self.block, self.enigma_name)
            if EnigmaManager.getSceneActiveEnigma() == self.enigma_name:
                SystemCameraManipulation.setBlockHotspot(self.block, False)

        if self.reset is True:
            SystemCameraManipulation.resetZoom()

    def _onGenerate(self, source):
        source.addFunction(self._toggle)