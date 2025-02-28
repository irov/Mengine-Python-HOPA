from Foundation.ArrowManager import ArrowManager
from Foundation.GuardBlockInput import GuardBlockInput
from Foundation.PolicyManager import PolicyManager
from Foundation.Task.TaskAlias import TaskAlias
from HOPA.ItemManager import ItemManager


class AliasInventoryAddInventoryItemFromPoint(TaskAlias):
    def _onParams(self, params):
        super(AliasInventoryAddInventoryItemFromPoint, self)._onParams(params)

        self.Inventory = params.get("Inventory")
        self.ItemName = params.get("ItemName")
        self.FromPoint = params.get("FromPoint")
        pass

    def _onGenerate(self, source):
        source.addFunction(self.Inventory.BlockButtons)

        InventoryItem = ItemManager.getItemInventoryItem(self.ItemName)

        if ArrowManager.emptyArrowAttach() is False:
            source.addTask("AliasInventoryReturnInventoryItem", Inventory=self.Inventory)
            pass

        CurrentSlotIndex = self.Inventory.getParam("CurrentSlotIndex")
        InventoryItems = self.Inventory.getParam("InventoryItems")
        SlotCount = self.Inventory.getParam("SlotCount")

        if self.Inventory.hasInventoryItem(InventoryItem) is False:
            InventoryItemIndex = len(InventoryItems)
        else:
            InventoryItemIndex = self.Inventory.indexInventoryItem(InventoryItem)
            pass

        NewSlotIndex = int(InventoryItemIndex / SlotCount) * SlotCount
        if CurrentSlotIndex != NewSlotIndex:
            with GuardBlockInput(source) as guard_source:
                guard_source.addTask("TaskInventorySlotsHideInventoryItem", Inventory=self.Inventory)
                guard_source.addTask("TaskInventoryCurrentSlotIndex", Inventory=self.Inventory, Value=NewSlotIndex)
                guard_source.addTask("TaskInventorySlotsShowInventoryItem", Inventory=self.Inventory)
                pass
            pass
        pass

        # - fix for PopUp items -----------------------------
        # * CountItem issue:
        # - popup item need to be updated for displaying actual count
        # PopUpInventoryItem = PopUpItemManager.getItemInventoryItem(self.ItemName)
        # if PopUpInventoryItem is not None:
        #     source.addTask("TaskAppendParam", Object = PopUpInventoryItem, Param = "FoundItems", Value = self.ItemName)
        # ---------------------------------------------------

        hasInventoryItem = self.Inventory.hasInventoryItem(InventoryItem)

        if hasInventoryItem is False:
            source.addTask("TaskInventoryAddItem", Inventory=self.Inventory, ItemName=self.ItemName)
            source.addTask("TaskInventorySlotAddInventoryItem", Inventory=self.Inventory, InventoryItem=InventoryItem)
            source.addDisable(InventoryItem)
        # - old functionality ------------------------------
        # - moved after EffectInventoryAddInventoryItem
        # - because before Effect we do not have to update
        # FoundItems in InventoryItem (???)
        # --------------------------------------------------
        else:
            source.addTask("TaskAppendParam", Object=InventoryItem, Param="FoundItems", Value=self.ItemName)
            pass
        # --------------------------------------------------

        EffectInventoryAddInventoryItem = PolicyManager.getPolicy("EffectInventoryAddInventoryItemFromPoint",
                                                                  "TaskEffectInventoryAddInventoryItem")

        # - effect for InventoryCountItem ------------------
        # - dummy count item check
        # --------------------------------------------------
        if InventoryItem.hasParam("FontName") is True:
            EffectInventoryAddInventoryItem = PolicyManager.getPolicy("EffectInventoryAddInventoryCountItemFromPoint",
                                                                      "TaskEffectInventoryAddInventoryItem")
        # --------------------------------------------------

        source.addTask(EffectInventoryAddInventoryItem, Inventory=self.Inventory, InventoryItem=InventoryItem,
                       FromPoint=self.FromPoint)

        # - fix for CountItem ------------------------------
        # - old code that was before EffectInventoryAddInventoryItem
        # --------------------------------------------------
        # if hasInventoryItem is True:
        #     source.addTask("TaskAppendParam", Object = InventoryItem, Param = "FoundItems", Value = self.ItemName)
        # --------------------------------------------------

        if hasInventoryItem is False:
            source.addEnable(InventoryItem)
            pass

        if Mengine.hasResource("ItemToSlot") is True:
            source.addTask("TaskSoundEffect", SoundName="ItemToSlot", Wait=False)
            pass

        source.addNotify(Notificator.onInventoryAddItem, self.Inventory, InventoryItem)
        source.addFunction(self.Inventory.UnBlockButtons)
