from HOPA.EnigmaManager import EnigmaManager
from HOPA.HOGFittingItemManager import HOGFittingItemManager
from HOPA.Macro.MacroCommand import MacroCommand

class MacroHOGFittingQueueAddItem(MacroCommand):

    def _onValues(self, values):
        self.EnigmaName = values[0]
        self.ItemName = values[1]

    def _onInitialize(self):
        if _DEVELOPMENT is True:
            if EnigmaManager.hasEnigma(self.EnigmaName) is False:
                self.initializeFailed("HOGFittingPickItem Enigma %s not found in Params" % self.EnigmaName)

            if HOGFittingItemManager.hasItem(self.ItemName) is False:
                self.initializeFailed("HOGFittingPickItem Item %s not found in Params" % self.ItemName)

    def _onGenerate(self, source):
        Enigma = EnigmaManager.getEnigmaObject(self.EnigmaName)

        source.addFunction(Enigma.appendParam, "QueueItems", self.ItemName)