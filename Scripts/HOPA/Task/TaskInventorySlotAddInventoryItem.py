from Foundation.Task.TaskAlias import TaskAlias

class TaskInventorySlotAddInventoryItem(TaskAlias):
    def _onParams(self, params):
        super(TaskInventorySlotAddInventoryItem, self)._onParams(params)
        self.InventoryItem = params.get("InventoryItem")
        self.Inventory = params.get("Inventory")
        pass

    def _onGenerate(self, source):
        SlotID = self.Inventory.getFreeSlotID(self.InventoryItem)

        source.addTask("TaskInventorySlotSetItem", Inventory=self.Inventory, SlotID=SlotID, InventoryItem=self.InventoryItem)
        pass
    pass