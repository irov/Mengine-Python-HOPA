from Foundation.GuardBlockInput import GuardBlockInput
from Foundation.Task.TaskAlias import TaskAlias


class AliasInventoryRemoveAttachInventoryItem(TaskAlias):
    def _onParams(self, params):
        super(AliasInventoryRemoveAttachInventoryItem, self)._onParams(params)

        self.InventoryItem = params.get("InventoryItem")
        self.Inventory = params.get("Inventory")

    def _onInitialize(self):
        super(AliasInventoryRemoveAttachInventoryItem, self)._onInitialize()

        InventoryItems = self.Inventory.getParam("InventoryItems")

        if _DEVELOPMENT is True:
            if self.InventoryItem not in InventoryItems:
                self.initializeFailed("InventoryItem %s not found in Inventory %s", self.InventoryItem, self.Inventory.name)

    def _onGenerate(self, source):
        CurrentSlotIndex = self.Inventory.getParam("CurrentSlotIndex")
        InventoryItems = self.Inventory.getParam("InventoryItems")
        SlotCount = self.Inventory.getParam("SlotCount")

        InventoryItemRemoveIndex = InventoryItems.index(self.InventoryItem)

        RemoveSlotIndex = int(InventoryItemRemoveIndex / SlotCount) * SlotCount

        source.addTask("TaskEnable", Object=self.InventoryItem, Value=False)
        source.addTask("TaskRemoveArrowAttach")
        source.addTask("TaskSceneLayerAddEntity", LayerName="InventoryItemEffect", Object=self.InventoryItem,
                       AdaptScreen=True)

        with GuardBlockInput(source) as guard_source:
            if CurrentSlotIndex != RemoveSlotIndex:
                guard_source.addTask("TaskInventorySlotsHideInventoryItem", Inventory=self.Inventory)
                guard_source.addTask("TaskDelParam", Object=self.Inventory, Param="InventoryItems", Value=self.InventoryItem)
                guard_source.addTask("TaskInventorySlotsShowInventoryItem", Inventory=self.Inventory)
            else:
                guard_source.addTask("TaskInventorySlotsHideInventoryItem", Inventory=self.Inventory,
                                     From=InventoryItemRemoveIndex - RemoveSlotIndex + 1)

                guard_source.addTask("TaskDelParam", Object=self.Inventory, Param="InventoryItems",
                                     Value=self.InventoryItem)

                guard_source.addTask("TaskInventorySlotsShowInventoryItem", Inventory=self.Inventory,
                                     From=InventoryItemRemoveIndex - RemoveSlotIndex)

        source.addTask("TaskObjectReturn", Object=self.InventoryItem)

        source.addTask("TaskNotify", ID=Notificator.onInventoryRemoveInventoryItem,
                       Args=(self.Inventory, self.InventoryItem))
