from Foundation.DemonManager import DemonManager
from HOPA.ItemManager import ItemManager
from HOPA.Macro.MacroCommand import MacroCommand


class MacroItemAddAttachFX(MacroCommand):
    def _onValues(self, values):
        self.ItemName = values[0]

    def _onInitialize(self):
        if _DEVELOPMENT is True:
            if self.ItemName is None:
                self.initializeFailed("Item is None")

            if ItemManager.hasItem(self.ItemName) is False:
                self.initializeFailed("Item %s not found" % (self.ItemName))

            if ItemManager.hasItemInventoryItem(self.ItemName) is False:
                self.initializeFailed("Item %s not have InventoryName" % (self.ItemName))

    def _onGenerate(self, source):
        Inventory = DemonManager.getDemon("Inventory")
        InventoryItem = ItemManager.getItemInventoryItem(self.ItemName)

        def __this(item):
            if item is InventoryItem:
                return True
            return False

        source.addTask("TaskInventoryAddItem", Inventory=Inventory, ItemName=self.ItemName, ItemHide=True)
        # source.addListener(Notificator.onInventoryAppendInventoryItem, Filter = __this)
        source.addDelay(0.1 * 1000)  # speed fix
        source.addTask("TaskInventorySlotAddInventoryItem", Inventory=Inventory, InventoryItem=InventoryItem)
        source.addTask("AliasInventoryItemAttach", InventoryItem=InventoryItem)

