from Foundation.Task.TaskAlias import TaskAlias
from HOPA.FittingInventoryManager import FittingInventoryManager
from HOPA.ItemManager import ItemManager

class AliasFittingInventoryAddInventoryItem(TaskAlias):
    def _onParams(self, params):
        super(AliasFittingInventoryAddInventoryItem, self)._onParams(params)

        self.FittingInventory = params.get("FittingInventory")
        self.ItemName = params.get("ItemName")
        pass

    def _onGenerate(self, source):
        # if ArrowManager.emptyArrowAttach() is False:
        # source.addTask("AliasFittingInventoryReturnInventoryItem", Inventory = self.Inventory)
        # pass
        InventoryItem = ItemManager.getItemInventoryItem(self.ItemName)

        if self.FittingInventory.hasFitting(InventoryItem) == False:
            Slot = FittingInventoryManager.s_slots[self.ItemName]
            SlotIndex = Slot.getIndex()
            source.addTask("TaskFittingInventoryAddFitting", FittingInventory=self.FittingInventory, SlotIndex=SlotIndex, InventoryItem=InventoryItem)
            pass

        AddSlotIndex = self.FittingInventory.getFittingIndex(InventoryItem)

        source.addTask("TaskEffectFittingInventoryAddInventoryItem", FittingInventory=self.FittingInventory, SlotID=AddSlotIndex, ItemName=self.ItemName)
        source.addTask("TaskFittingInventoryAddInventoryItem", FittingInventory=self.FittingInventory, InventoryItem=InventoryItem)
        pass

    pass