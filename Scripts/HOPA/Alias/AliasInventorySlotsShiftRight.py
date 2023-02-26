from Foundation.ArrowManager import ArrowManager
from Foundation.GuardBlockInput import GuardBlockInput
from Foundation.Task.TaskAlias import TaskAlias

class AliasInventorySlotsShiftRight(TaskAlias):
    def _onParams(self, params):
        super(AliasInventorySlotsShiftRight, self)._onParams(params)
        self.Inventory = params.get("Inventory")
        self.NewSlotIndex = params.get("NewSlotIndex", None)
        self.Count = params.get("Count", None)

    def _onGenerate(self, source):
        CurrentSlotIndex = self.Inventory.getParam("CurrentSlotIndex")
        InventoryItems = self.Inventory.getParam("InventoryItems")
        SlotCount = self.Inventory.getParam("SlotCount")
        Except = None

        if ArrowManager.emptyArrowAttach() is False:
            InventoryItem = ArrowManager.getArrowAttach()

            if InventoryItem.getType() == 'ObjectInventoryItem':
                Except = [InventoryItem]

        Index = int(CurrentSlotIndex / SlotCount)
        InventoryItemsCount = len(InventoryItems)
        MaxIndex = int(InventoryItemsCount / SlotCount)

        if Index == MaxIndex:
            return

        if self.NewSlotIndex is None:
            self.NewSlotIndex = (Index + 1) * SlotCount

        if self.NewSlotIndex >= InventoryItemsCount:
            return

        with GuardBlockInput(source) as guard_source:
            guard_source.addTask("TaskInventorySlotsHideInventoryItem", Inventory=self.Inventory, Except=Except)
            guard_source.addTask("TaskInventoryCurrentSlotIndex", Inventory=self.Inventory, Value=self.NewSlotIndex)
            guard_source.addTask("TaskInventorySlotsShowInventoryItem", Inventory=self.Inventory, Except=Except)