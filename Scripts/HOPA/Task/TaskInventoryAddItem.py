from Foundation.Task.Task import Task

from HOPA.ItemManager import ItemManager


class TaskInventoryAddItem(Task):
    Skiped = True

    def _onParams(self, params):
        super(TaskInventoryAddItem, self)._onParams(params)
        self.Inventory = params.get("Inventory")
        self.ItemName = params.get("ItemName")
        self.ItemHide = params.get("ItemHide", False)
        pass

    def _onInitialize(self):
        super(TaskInventoryAddItem, self)._onInitialize()

        if _DEVELOPMENT is True:
            if self.ItemName is None:
                self.initializeFailed("itemName is None")
                pass
            pass
        pass

    def _onRun(self):
        InventoryItem = ItemManager.getItemInventoryItem(self.ItemName)
        InventoryItem.appendParam("FoundItems", self.ItemName)

        # hack for popup item
        # from HOPA.PopUpItemManager import PopUpItemManager
        # PopupInventoryItem = PopUpItemManager.getItemInventoryItem(self.ItemName)
        # PopupInventoryItem.appendParam("FoundItems", self.ItemName)

        self.Inventory.addInventoryItem(InventoryItem)

        if self.ItemHide is False:
            return True
            pass

        SlotsCount = self.Inventory.getSlotCount()
        InventoryItems = self.Inventory.getInventoryItems()
        CountInventoryItems = len(InventoryItems)

        if CountInventoryItems > SlotsCount and InventoryItem.isActive() is True:
            entity = InventoryItem.getEntity()
            entity.disable()
            pass

        return True
        pass

    pass
