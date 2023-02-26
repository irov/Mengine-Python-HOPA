from Foundation.DemonManager import DemonManager
from HOPA.ItemManager import ItemManager
from HOPA.Macro.MacroCommand import MacroCommand

class MacroChangeItemFX(MacroCommand):
    def _onValues(self, values):
        self.ItemNameFrom = values[0]
        self.ItemNameTo = values[1]
        pass

    def _onInitialize(self):
        if _DEVELOPMENT is True:
            if self.ItemNameFrom is None:
                self.initializeFailed("ItemNameFrom is None")
                pass

            if self.ItemNameTo is None:
                self.initializeFailed("ItemNameTo is None")
                pass

            if ItemManager.hasItem(self.ItemNameFrom) is False:
                self.initializeFailed("ItemNameFrom %s not found" % (self.ItemNameFrom,))
                pass

            if ItemManager.hasItemInventoryItem(self.ItemNameFrom) is False:
                self.initializeFailed("ItemNameFrom %s not have InventoryName" % (self.ItemNameFrom,))
                pass

            if ItemManager.hasItem(self.ItemNameTo) is False:
                self.initializeFailed("ItemNameTo %s not found" % (self.ItemNameTo,))
                pass

            if ItemManager.hasItemInventoryItem(self.ItemNameTo) is False:
                self.initializeFailed("ItemNameTo %s not have InventoryName" % (self.ItemNameTo,))
                pass
            pass
        pass

    def _onGenerate(self, source):
        InventoryItemFrom = ItemManager.getItemInventoryItem(self.ItemNameFrom)

        Inventory = DemonManager.getDemon("Inventory")

        source.addTask("AliasInventoryRemoveInventoryItemFX", Inventory=Inventory, InventoryItem=InventoryItemFrom)
        source.addTask("AliasInventoryGetInventoryItem", ItemName=self.ItemNameTo)

        pass
    pass