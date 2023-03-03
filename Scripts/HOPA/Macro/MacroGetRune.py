from Foundation.DemonManager import DemonManager
from HOPA.Macro.MacroCommand import MacroCommand


class MacroGetRune(MacroCommand):
    def _onValues(self, values):
        self.RuneID = values[0]
        pass

    def _onInitialize(self):
        pass

    def _onGenerate(self, source):
        source.addFunction(self._Set_New_Rune)
        pass

    def _Set_New_Rune(self):
        DemonMagicGlove = DemonManager.getDemon('MagicGlove')
        DemonMagicGlove.appendParam("Runes", self.RuneID)

    pass
