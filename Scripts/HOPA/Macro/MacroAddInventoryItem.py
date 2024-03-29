from Foundation.DemonManager import DemonManager
from HOPA.ItemManager import ItemManager
from HOPA.Macro.MacroCommand import MacroCommand


class MacroAddInventoryItem(MacroCommand):
    def _onValues(self, values, **params):
        self.ItemName = values[0]
        pass

    def _onInitialize(self, **params):
        if _DEVELOPMENT is True:
            if self.ItemName is None:
                self.initializeFailed("Item is None")

            if ItemManager.hasItemInventoryItem(self.ItemName) is False:
                self.initializeFailed("Item %s not have InventoryName" % (self.ItemName))

    def _onGenerate(self, source):
        # print "MacroAddInventoryItem", self.ItemName
        Inventory = DemonManager.getDemon("Inventory")

        InventoryItem = ItemManager.getItemInventoryItem(self.ItemName)

        source.addFunction(Inventory.BlockButtons)

        source.addTask("TaskInventoryAddItem", Inventory=Inventory, ItemName=self.ItemName, ItemHide=True)
        source.addTask("TaskInventorySlotAddInventoryItem", Inventory=Inventory, InventoryItem=InventoryItem)

        source.addFunction(Inventory.UnBlockButtons)
