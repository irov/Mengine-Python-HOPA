from Foundation.Task.Task import Task


class TaskInventoryAddInventoryItem(Task):
    Skiped = True

    def _onParams(self, params):
        super(TaskInventoryAddInventoryItem, self)._onParams(params)

        self.inventoryItem = params.get("InventoryItem")
        self.Inventory = params.get("Inventory")
        pass

    def _onInitialize(self):
        super(TaskInventoryAddInventoryItem, self)._onInitialize()

        if _DEVELOPMENT is True:
            if self.inventoryItem is None:
                self.initializeFailed("itemName is None")
                pass
            pass
        pass

    def _onRun(self):
        self.Inventory.appendParam("InventoryItems", self.inventoryItem)
        #        self.Inventory.addInventoryItem( self.inventoryItemName )
        return True
        pass

    pass
