from HOPA.EnigmaManager import EnigmaManager
from HOPA.HOGFittingItemManager import HOGFittingItemManager
from HOPA.Macro.MacroCommand import MacroCommand


class MacroHOGFittingRemoveItem(MacroCommand):
    def _onValues(self, values):
        self.EnigmaName = values[0]
        self.ItemName = values[1]
        pass

    def _onInitialize(self):
        if _DEVELOPMENT is True:
            if EnigmaManager.hasEnigma(self.EnigmaName) is False:
                self.initializeFailed("HOGFittingRemoveItem Enigma %s not found in Params" % (self.EnigmaName))
                pass

            if HOGFittingItemManager.hasItem(self.ItemName) is False:
                self.initializeFailed("HOGFittingRemoveItem Item %s not found in Params" % (self.ItemName))
                pass
            pass
        pass

    def _onGenerate(self, source):
        Enigma = EnigmaManager.getEnigmaObject(self.EnigmaName)

        def RemoveItem():
            Enigma.delParam("Items", self.ItemName)
            pass

        source.addFunction(RemoveItem)
        pass

    pass
