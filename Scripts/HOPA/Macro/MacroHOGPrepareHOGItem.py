from HOPA.EnigmaManager import EnigmaManager
from HOPA.Macro.MacroCommand import MacroCommand


class MacroHOGPrepareHOGItem(MacroCommand):
    def _onValues(self, values):
        self.EnigmaName = values[0]
        self.ItemName = values[1]
        pass

    def _onGenerate(self, source):
        Enigma = EnigmaManager.getEnigmaObject(self.EnigmaName)

        def addItemToSlot():
            Enigma.appendParam("PrepareItems", self.ItemName)
            pass

        source.addFunction(addItemToSlot)
        pass
