from Foundation.Task.Task import Task


class TaskArrowAttachInventoryItem(Task):
    # Skiped = True

    def _onParams(self, params):
        super(TaskArrowAttachInventoryItem, self)._onParams(params)
        self.Inventory = params.get("Inventory")
        self.InventoryItem = params.get("InventoryItem")
        pass

    def _onRun(self):
        InventoryEntity = self.Inventory.getEntity()
        slot = InventoryEntity.findSlot(self.InventoryItem)
        slotID = slot.getSlotID()
        InventoryEntity.pickInventoryItem(slotID)
        return True
        pass

    pass
