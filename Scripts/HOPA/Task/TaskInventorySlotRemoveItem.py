from Foundation.Task.Task import Task


class TaskInventorySlotRemoveItem(Task):
    Skiped = True

    def _onParams(self, params):
        super(TaskInventorySlotRemoveItem, self)._onParams(params)
        self.Inventory = params.get("Inventory")
        self.SlotID = params.get("SlotID")
        pass

    def _onInitialize(self):
        super(TaskInventorySlotRemoveItem, self)._onInitialize()
        pass

    def _onRun(self):
        InventoryEntity = self.Inventory.getEntity()

        slots = InventoryEntity.getSlots()
        slot = slots[self.SlotID]

        if slot.item is None:
            return True
            pass

        RemoveItem = slot.removeItem()

        if RemoveItem is None:
            self.log("slot %d is empty" % (self.SlotID))
            return True
            pass

        RemoveItem.setEnable(False)

        return True
        pass

    pass
