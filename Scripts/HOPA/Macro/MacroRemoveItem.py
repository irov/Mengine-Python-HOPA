from Foundation.DemonManager import DemonManager
from HOPA.ItemManager import ItemManager
from HOPA.Macro.MacroCommand import MacroCommand


class MacroRemoveItem(MacroCommand):
    def _onValues(self, values):
        self.ItemName = values[0]
        pass

    def _onInitialize(self):
        if _DEVELOPMENT is True:
            if self.ItemName is None:
                self.initializeFailed("Item is None")
                pass

            if ItemManager.hasItem(self.ItemName) is False:
                self.initializeFailed("Item %s not found" % (self.ItemName))
                pass

            if ItemManager.hasItemInventoryItem(self.ItemName) is False:
                self.initializeFailed("Item %s not have InventoryName" % (self.ItemName))
                pass
            pass
        pass

    def _onGenerate(self, source):
        InventoryItem = ItemManager.getItemInventoryItem(self.ItemName)

        Inventory = DemonManager.getDemon("Inventory")
        source.addTask("AliasInventoryRemoveInventoryItem", Inventory=Inventory, InventoryItem=InventoryItem)
        pass

    pass
