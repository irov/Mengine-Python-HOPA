from Foundation.GuardBlockInput import GuardBlockInput
from Foundation.Task.TaskAlias import TaskAlias

class AliasInventoryShowCurrentSlots(TaskAlias):
    def _onParams(self, params):
        super(AliasInventoryShowCurrentSlots, self)._onParams(params)

        self.Inventory = params.get("Inventory")
        pass

    def _onGenerate(self, source):
        CurrentSlotIndex = self.Inventory.getParam("CurrentSlotIndex")
        InventoryItems = self.Inventory.getParam("InventoryItems")
        SlotCount = self.Inventory.getParam("SlotCount")

        if CurrentSlotIndex + SlotCount > len(InventoryItems):
            CurrentSlotIndex = max(len(InventoryItems) - SlotCount, 0)
            pass

        with GuardBlockInput(source) as guard_source:
            guard_source.addTask("TaskInventoryCurrentSlotIndex", Inventory=self.Inventory, Value=CurrentSlotIndex)
            guard_source.addTask("TaskInventorySlotsShowInventoryItem", Inventory=self.Inventory)
            pass
        pass

    pass