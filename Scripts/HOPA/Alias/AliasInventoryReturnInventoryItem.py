from Foundation.ArrowManager import ArrowManager
from Foundation.GuardBlockInput import GuardBlockInput
from Foundation.Task.TaskAlias import TaskAlias


class AliasInventoryReturnInventoryItem(TaskAlias):
    def _onParams(self, params):
        super(AliasInventoryReturnInventoryItem, self)._onParams(params)

        self.Inventory = params.get("Inventory")
        self.UnblockInventory = params.get("UnblockInventory", False)
        self.Return = params.get("Return", True)

    def _onInitialize(self):
        super(AliasInventoryReturnInventoryItem, self)._onInitialize()

        if _DEVELOPMENT is True:
            if ArrowManager.emptyArrowAttach() is True:
                self.initializeFailed("AliasInventoryReturnInventoryItem Attach not found")

    def _onGenerate(self, source):
        InventoryItem = ArrowManager.getArrowAttach()
        InventoryItems = self.Inventory.getParam("InventoryItems")
        self.Inventory.setParam("BlockScrolling", True)
        if InventoryItem not in InventoryItems:
            InventoryItem.setEnable(False)
            return

        source.addTask("TaskRemoveArrowAttach")

        if self.Return is True:
            CurrentSlotIndex = self.Inventory.getParam("CurrentSlotIndex")
            InventoryItems = self.Inventory.getParam("InventoryItems")
            SlotCount = self.Inventory.getParam("SlotCount")

            InventoryItemReturnIndex = InventoryItems.index(InventoryItem)
            ReturnSlotIndex = int(InventoryItemReturnIndex / SlotCount) * SlotCount

            SetSlotIndex = InventoryItemReturnIndex - ReturnSlotIndex

            if Mengine.hasTouchpad() is False:  # Click&Click doesn't need this
                source.addTask("TaskSceneLayerAddEntity", LayerName="InventoryItemEffect",
                               Object=InventoryItem, AdaptScreen=True)

            if CurrentSlotIndex != ReturnSlotIndex:
                with GuardBlockInput(source) as guard_source:
                    guard_source.addTask("TaskInventorySlotsHideInventoryItem", Inventory=self.Inventory, Except=[InventoryItem])
                    guard_source.addTask("TaskInventoryCurrentSlotIndex", Inventory=self.Inventory, Value=ReturnSlotIndex)
                    guard_source.addTask("TaskInventorySlotsShowInventoryItem", Inventory=self.Inventory, Except=[InventoryItem])

            if Mengine.hasTouchpad() is False:  # Click&Click doesn't need this
                source.addTask("AliasEffectInventoryReturnInventoryItem", Inventory=self.Inventory, SlotID=SetSlotIndex,
                               InventoryItem=InventoryItem)

            source.addTask("TaskObjectReturn", Object=InventoryItem)

            source.addNotify(Notificator.onInventoryReturnInventoryItem, self.Inventory, InventoryItem)
            source.addTask("TaskInventorySlotReturnItem", Inventory=self.Inventory, InventoryItem=InventoryItem)
            # source.addTask("TaskNotify", ID=Notificator.onInventoryReturnInventoryItem,
            #                Args=(self.Inventory, InventoryItem))

        if self.UnblockInventory is True:
            source.addTask("TaskInventoryDetachItem", Inventory=self.Inventory, InventoryItem=InventoryItem)

        source.addFunction(self.Inventory.setParam, "BlockScrolling", False)
