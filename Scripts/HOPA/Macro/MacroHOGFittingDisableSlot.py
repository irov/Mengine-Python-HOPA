from HOPA.EnigmaManager import EnigmaManager
from HOPA.HOGFittingItemManager import HOGFittingItemManager
from HOPA.Macro.MacroCommand import MacroCommand


class MacroHOGFittingDisableSlot(MacroCommand):
    def _onValues(self, values):
        self.EnigmaName = values[0]
        self.ItemName = values[1]
        pass

    def _onInitialize(self):
        if _DEVELOPMENT is True:
            if HOGFittingItemManager.hasItem(self.ItemName) is False:
                self.initializeFailed("HOGFittingFindItem Item %s not found in Params" % (self.ItemName))
                pass
            pass
        pass

    def _onGenerate(self, source):
        Enigma = EnigmaManager.getEnigmaObject(self.EnigmaName)
        EnigmaEntity = Enigma.getEntity()
        Inventory = EnigmaEntity.getInventory()

        # Inventory = DemonManager.getDemon("HOGInventoryFitting")

        def ff():
            Inventory.getEntity().DisableSlotItem(self.ItemName)
            pass

        source.addFunction(ff)
        pass

    pass
