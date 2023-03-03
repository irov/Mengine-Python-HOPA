from Foundation.Task.TaskAlias import TaskAlias


class AliasInventorySlotsMoveRemoveItem(TaskAlias):
    def _onParams(self, params):
        super(AliasInventorySlotsMoveRemoveItem, self)._onParams(params)

        self.Inventory = params.get("Inventory")
        self.InventoryItem = params.get("InventoryItem")

    def _onGenerate(self, source):
        InventoryItem = self.InventoryItem

        InventoryItems = self.Inventory.getParam("InventoryItems")
        InventoryItemsCount = len(InventoryItems)
        SlotCount = self.Inventory.getParam("SlotCount")

        InventoryItemReturnIndex = InventoryItems.index(InventoryItem)
        ReturnSlotIndex = int(InventoryItemReturnIndex / SlotCount) * SlotCount
        CurrentSlotIndex = self.Inventory.getCurrentSlotIndex()

        curItemIndex = InventoryItemReturnIndex - CurrentSlotIndex

        source.addTask("TaskDelParam", Object=self.Inventory, Param="InventoryItems", Value=self.InventoryItem)

        if InventoryItemReturnIndex == InventoryItemsCount - 1 and InventoryItemsCount <= SlotCount:
            return
            pass

        if ReturnSlotIndex - CurrentSlotIndex <= InventoryItemsCount - CurrentSlotIndex and InventoryItemsCount <= CurrentSlotIndex + SlotCount and CurrentSlotIndex > 0:
            Exceptions = []
            for i in range(curItemIndex, SlotCount):
                slot = self.Inventory.getSlot(i)
                invItem = slot.getItem()
                Exceptions.append(invItem)
                pass

            source.addTask("AliasInventorySlotsMoveRight", Inventory=self.Inventory, Exceptions=Exceptions)
            pass

        elif ReturnSlotIndex <= InventoryItemsCount - 1:
            StartSlotIndex = curItemIndex + 1
            newIndex = min(SlotCount, StartSlotIndex)
            Exceptions = []
            for i in range(0, newIndex):
                slot = self.Inventory.getSlot(i)
                if slot is None:
                    newIndex -= 1
                    continue
                    pass
                invItem = slot.getItem()
                Exceptions.append(invItem)
                pass
            source.addTask("AliasInventorySlotsMoveLeft", Inventory=self.Inventory, StartSlotIndex=newIndex, Exceptions=Exceptions)
