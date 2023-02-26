from HOPA.EnigmaManager import EnigmaManager
from HOPA.HOGFittingItemManager import HOGFittingItemManager
from HOPA.Macro.MacroCommand import MacroCommand

class MacroHOGFittingAddItem(MacroCommand):
    def _onValues(self, values):
        self.EnigmaName = values[0]
        self.ItemName = values[1]
        pass

    def _onInitialize(self):
        if _DEVELOPMENT is True:
            if EnigmaManager.hasEnigma(self.EnigmaName) is False:
                self.initializeFailed("HOGFittingPickItem Enigma %s not found in Params" % (self.EnigmaName))
                pass

            if HOGFittingItemManager.hasItem(self.ItemName) is False:
                self.initializeFailed("HOGFittingPickItem Item %s not found in Params" % (self.ItemName))
                pass
            pass
        pass

    def _onGenerate(self, source):
        Enigma = EnigmaManager.getEnigmaObject(self.EnigmaName)

        source.addFunction(Enigma.appendParam, "Items", self.ItemName)
        pass

    pass