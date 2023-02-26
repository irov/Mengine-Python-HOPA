from Foundation.Task.TaskAlias import TaskAlias
from HOPA.FittingInventoryManager import FittingInventoryManager
from HOPA.ItemManager import ItemManager

class AliasFittingInventoryGetInventoryItem(TaskAlias):
    def _onParams(self, params):
        super(AliasFittingInventoryGetInventoryItem, self)._onParams(params)

        self.FittingInventory = params.get("FittingInventory")
        self.ItemName = params.get("ItemName")
        pass

    def _onGenerate(self, source):
        InventoryItem = ItemManager.getItemInventoryItem(self.ItemName)

        if self.FittingInventory.hasFitting(InventoryItem) == False:
            Slot = FittingInventoryManager.s_slots[self.ItemName]
            SlotIndex = Slot.getIndex()
            source.addTask("TaskFittingInventoryAddFitting", FittingInventory=self.FittingInventory, SlotIndex=SlotIndex, InventoryItem=InventoryItem)
            pass

        AddSlotIndex = self.FittingInventory.getFittingIndex(InventoryItem)

        source.addTask("AliasFadeIn", FadeGroupName="FadeDialog", To=0.25, Time=0.2 * 1000, Block=False)  # speed fix
        source.addTask("TaskSceneLayerGroupEnable", LayerName="ItemPopUp", Value=True)
        source.addTask("TaskItemPopUp", GroupName="ItemPopUp", ItemName=self.ItemName)
        source.addTask("TaskSceneLayerGroupEnable", LayerName="ItemPopUp", Value=False)

        source.addTask("TaskEffectFittingInventoryGetInventoryItem", FittingInventory=self.FittingInventory, SlotID=AddSlotIndex, InventoryItem=InventoryItem)
        source.addTask("TaskFittingInventoryAddInventoryItem", FittingInventory=self.FittingInventory, InventoryItem=InventoryItem)

        source.addTask("AliasFadeOut", FadeGroupName="FadeDialog", From=0.25, Time=0.25 * 1000, Unblock=False)  # speed fix
        pass
    pass