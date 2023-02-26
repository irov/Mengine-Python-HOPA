from Foundation.Notificator import Notificator
from Foundation.PolicyManager import PolicyManager
from Foundation.Task.TaskAlias import TaskAlias
from HOPA.ItemManager import ItemManager

class AliasInventoryAddInventoryItem(TaskAlias):
    def _onParams(self, params):
        super(AliasInventoryAddInventoryItem, self)._onParams(params)

        self.Inventory = params.get("Inventory")
        self.ItemName = params.get("ItemName")

    def _onGenerate(self, source):
        source.addFunction(self.Inventory.BlockButtons)
        InventoryItem = ItemManager.getItemInventoryItem(self.ItemName)

        # if ArrowManager.emptyArrowAttach() is False:
        #     source.addTask("AliasInventoryReturnInventoryItem", Inventory=self.Inventory)

        CurrentSlotIndex = self.Inventory.getParam("CurrentSlotIndex")
        InventoryItems = self.Inventory.getParam("InventoryItems")
        SlotCount = self.Inventory.getParam("SlotCount")

        if self.Inventory.hasInventoryItem(InventoryItem) is False:
            InventoryItemIndex = len(InventoryItems)
        else:
            InventoryItemIndex = self.Inventory.indexInventoryItem(InventoryItem)

        NewSlotIndex = int(InventoryItemIndex / SlotCount) * SlotCount
        if CurrentSlotIndex != NewSlotIndex:
            PolicyInventoryChangeCurrentSlotIndex = PolicyManager.getPolicy("InventoryChangeCurrentSlotIndex", "AliasInventoryChangeCurrentSlotIndex")
            source.addTask(PolicyInventoryChangeCurrentSlotIndex, Inventory=self.Inventory, ItemName=self.ItemName, NewSlotIndex=NewSlotIndex)

        hasInventoryItem = self.Inventory.hasInventoryItem(InventoryItem)

        if hasInventoryItem is False:
            source.addTask("TaskInventoryAddItem", Inventory=self.Inventory, ItemName=self.ItemName)
            source.addTask("TaskInventorySlotAddInventoryItem", Inventory=self.Inventory, InventoryItem=InventoryItem)
            source.addTask("TaskEnable", Object=InventoryItem, Value=False)

        else:
            source.addTask("TaskAppendParam", Object=InventoryItem, Param="FoundItems", Value=self.ItemName)

        EffectInventoryAddInventoryItem = PolicyManager.getPolicy("EffectInventoryAddInventoryItem", "TaskEffectInventoryAddInventoryItem")

        if InventoryItem.hasParam("FontName") is True:
            EffectInventoryAddInventoryItem = PolicyManager.getPolicy("EffectInventoryAddInventoryCountItem", "TaskEffectInventoryAddInventoryItem")

        source.addTask(EffectInventoryAddInventoryItem, Inventory=self.Inventory, ItemName=self.ItemName, hasInventoryItem=hasInventoryItem)

        if hasInventoryItem is False:
            source.addTask("TaskEnable", Object=InventoryItem, Value=True)

        if Mengine.hasResource("ItemToSlot") is True:
            source.addTask("TaskSoundEffect", SoundName="ItemToSlot", Wait=False)

        source.addTask("TaskNotify", ID=Notificator.onInventoryAddItem, Args=(self.Inventory, InventoryItem))

        source.addFunction(self.Inventory.UnBlockButtons)