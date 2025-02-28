from Foundation.ArrowManager import ArrowManager
from Foundation.GuardBlockInput import GuardBlockInput
from Foundation.Task.TaskAlias import TaskAlias


class AliasInventoryRemoveInventoryItem(TaskAlias):
    def _onParams(self, params):
        super(AliasInventoryRemoveInventoryItem, self)._onParams(params)

        self.InventoryItem = params.get("InventoryItem")
        self.Inventory = params.get("Inventory")

    def _onGenerate(self, source):
        if ArrowManager.emptyArrowAttach() is False:
            Attach = ArrowManager.getArrowAttach()
            if Attach is self.InventoryItem:
                source.addTask("AliasItemDetach", InventoryItem=self.InventoryItem, Return=False)

        CurrentSlotIndex = self.Inventory.getParam("CurrentSlotIndex")
        InventoryItems = self.Inventory.getParam("InventoryItems")
        SlotCount = self.Inventory.getParam("SlotCount")

        if self.InventoryItem not in InventoryItems:
            Trace.log("Notification", 0, "AliasInventoryRemoveInventoryItem._onGenerate Inventory %s not have InventoryItem %s" % (self.Inventory.getName(), self.InventoryItem.getName()))
            return

        InventoryItemRemoveIndex = InventoryItems.index(self.InventoryItem)

        RemoveSlotIndex = int(InventoryItemRemoveIndex / SlotCount) * SlotCount

        with GuardBlockInput(source) as guard_source:
            if CurrentSlotIndex != RemoveSlotIndex:
                guard_source.addTask("TaskInventorySlotsHideInventoryItem", Inventory=self.Inventory)
                guard_source.addTask("TaskInventoryCurrentSlotIndex", Inventory=self.Inventory, Value=RemoveSlotIndex)
                guard_source.addTask("TaskInventorySlotsShowInventoryItem", Inventory=self.Inventory)
                pass

            guard_source.addTask("TaskInventorySlotsHideInventoryItem", Inventory=self.Inventory,
                                 From=InventoryItemRemoveIndex - RemoveSlotIndex,
                                 To=InventoryItemRemoveIndex - RemoveSlotIndex + 1)

            guard_source.addTask("TaskInventorySlotsHideInventoryItem", Inventory=self.Inventory,
                                 From=InventoryItemRemoveIndex - RemoveSlotIndex + 1)

            guard_source.addTask("TaskDelParam", Object=self.Inventory, Param="InventoryItems",
                                 Value=self.InventoryItem)
            pass

        source.addTask("TaskObjectReturn", Object=self.InventoryItem)
        source.addDisable(self.InventoryItem)

        source.addTask("TaskInventorySlotsShowInventoryItem", Inventory=self.Inventory,
                       From=InventoryItemRemoveIndex - RemoveSlotIndex)

        source.addNotify(Notificator.onInventoryRemoveInventoryItem, self.Inventory, self.InventoryItem)
