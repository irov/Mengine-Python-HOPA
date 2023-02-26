from Foundation.DemonManager import DemonManager
from Foundation.GuardBlockInput import GuardBlockInput
from Foundation.Task.TaskAlias import TaskAlias

class PolicyInventoryScrollingDefault(TaskAlias):
    def _onParams(self, params):
        super(PolicyInventoryScrollingDefault, self)._onParams(params)
        self.Inventory = DemonManager.getDemon("Inventory")
        self.InventoryItem = params.get("InventoryItem")
        pass

    def _onGenerate(self, source):
        CurrentSlotIndex = self.Inventory.getParam("CurrentSlotIndex")
        SlotCount = self.Inventory.getParam("SlotCount")

        InventoryItemIndex = self.Inventory.indexInventoryItem(self.InventoryItem)
        NeedSlotIndex = int(InventoryItemIndex / SlotCount) * SlotCount

        if CurrentSlotIndex != NeedSlotIndex:
            with GuardBlockInput(source) as guard_source:
                guard_source.addTask("TaskInventorySlotsHideInventoryItem", Inventory=self.Inventory)
                guard_source.addTask("TaskInventoryCurrentSlotIndex", Inventory=self.Inventory, Value=NeedSlotIndex)
                guard_source.addTask("TaskInventorySlotsShowInventoryItem", Inventory=self.Inventory)
                pass
            pass
        pass
    pass