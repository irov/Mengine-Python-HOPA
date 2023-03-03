from Foundation.DefaultManager import DefaultManager
from Foundation.Task.TaskAlias import TaskAlias


class TaskInventorySlotsShowInventoryItem(TaskAlias):
    def _onParams(self, params):
        super(TaskInventorySlotsShowInventoryItem, self)._onParams(params)

        self.Inventory = params.get("Inventory")
        self.From = params.get("From", None)
        self.To = params.get("To", None)

        self.Except = params.get("Except", None)
        pass

    def _onGenerate(self, source):
        CurrentSlotIndex = self.Inventory.getParam("CurrentSlotIndex")
        InventoryItems = self.Inventory.getParam("InventoryItems")
        SlotCount = self.Inventory.getParam("SlotCount")

        InventoryItemsCount = len(InventoryItems)

        if InventoryItemsCount == 0:
            return
            pass

        ActiveSlotCount = min(InventoryItemsCount - CurrentSlotIndex, SlotCount)

        if self.To is not None:
            ActiveSlotCount = min(ActiveSlotCount, self.To)
            pass

        FromIndex = CurrentSlotIndex
        if self.From is not None:
            FromIndex += self.From
            pass

        ToIndex = CurrentSlotIndex + ActiveSlotCount

        ### Not active Inventory in MG fix
        if self.Inventory.isActive() is False:
            return
            pass
        ###

        InventoryEntity = self.Inventory.getEntity()
        slots = InventoryEntity.getSlots()

        with source.addParallelTask(ActiveSlotCount) as tcp:
            for tci, index in zip(tcp, range(FromIndex, ToIndex)):
                InventoryItem = InventoryItems[index]

                if self.Except is not None and InventoryItem in self.Except:
                    continue
                    pass

                SlotID = index - CurrentSlotIndex
                slot = slots[SlotID]

                returnItem = slot.getCursorItem()
                if returnItem is InventoryItem:
                    continue
                    pass

                tci.addTask("TaskInventorySlotSetItem", Inventory=self.Inventory, SlotID=SlotID,
                            InventoryItem=InventoryItem)

                InventoryItemEntityNode = InventoryItem.getEntityNode()

                time = DefaultManager.getDefault("InventoryShiftSpeed", 0.1)
                time *= 1000  # speed fix

                tci.addTask("TaskNodeAlphaTo", Node=InventoryItemEntityNode, Time=time, From=0.0, To=1.0)

