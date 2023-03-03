from Foundation.DemonManager import DemonManager
from HOPA.ItemManager import ItemManager
from HOPA.Macro.MacroCommand import MacroCommand


class MacroAddItemFX(MacroCommand):
    def _onValues(self, values, **params):
        self.ItemName = values[0]

    def _onInitialize(self, **params):
        if _DEVELOPMENT is True:
            if self.ItemName is None:
                self.initializeFailed("Item is None")

            if ItemManager.hasItem(self.ItemName) is False:
                self.initializeFailed("Item %s not found" % (self.ItemName,))

            if ItemManager.hasItemInventoryItem(self.ItemName) is False:
                self.initializeFailed("Item %s not have InventoryName" % (self.ItemName,))

    def _onGenerate(self, source):
        Inventory = DemonManager.getDemon("Inventory")

        source.addTask("AliasInventoryAddInventoryItemFX", Inventory=Inventory, ItemName=self.ItemName,
                       EffectPolicy="ActionPickItem")
