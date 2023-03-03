from Foundation.Task.TaskAlias import TaskAlias


class AliasInventorySlotsMoveAddItem(TaskAlias):
    def _onParams(self, params):
        super(AliasInventorySlotsMoveAddItem, self)._onParams(params)

        self.Inventory = params.get("Inventory")
        self.InventoryItem = params.get("InventoryItem")
        self.CurrentSlotIndex = params.get("CurrentSlotIndex")

    def _onGenerate(self, source):
        InventoryItem = self.InventoryItem

        CountRight = self.Inventory.getScrollCountRight(InventoryItem, self.CurrentSlotIndex)
        CountLeft = self.Inventory.getScrollCountLeft(InventoryItem, self.CurrentSlotIndex)

        if CountRight >= 1:
            speedFactor = CountRight
            Exceptions = []
            for i in xrange(CountRight):
                source.addTask("AliasInventorySlotsMoveRight", Inventory=self.Inventory,
                               SpeedFactor=speedFactor, Exceptions=Exceptions)

        elif CountLeft >= 1:
            speedFactor = CountLeft
            for i in xrange(CountLeft):
                source.addTask("AliasInventorySlotsMoveLeft", Inventory=self.Inventory, SpeedFactor=speedFactor,
                               Exceptions=(InventoryItem,))
