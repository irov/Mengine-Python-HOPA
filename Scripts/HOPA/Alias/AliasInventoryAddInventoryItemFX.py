from Foundation.ArrowManager import ArrowManager
from Foundation.Task.TaskAlias import TaskAlias
from HOPA.ItemManager import ItemManager


class AliasInventoryAddInventoryItemFX(TaskAlias):
    def _onParams(self, params):
        super(AliasInventoryAddInventoryItemFX, self)._onParams(params)

        self.Inventory = params.get("Inventory")
        self.ItemName = params.get("ItemName")
        self.EffectPolicy = params.get("EffectPolicy")
        pass

    def _onGenerate(self, source):
        source.addFunction(self.Inventory.BlockButtons)
        InventoryItem = ItemManager.getItemInventoryItem(self.ItemName)

        if ArrowManager.emptyArrowAttach() is False:
            source.addTask("AliasInventoryReturnInventoryItemFX", Inventory=self.Inventory)
            pass

        hasInventoryItem = self.Inventory.hasInventoryItem(InventoryItem)

        if hasInventoryItem is False:
            source.addTask("TaskInventoryAddItem", Inventory=self.Inventory, ItemName=self.ItemName)
            # source.addTask("TaskInventorySlotAddInventoryItem", Inventory = self.Inventory, InventoryItem = InventoryItem)
            source.addTask("TaskEnable", Object=InventoryItem, Value=False)
            pass
        else:
            source.addTask("TaskAppendParam", Object=InventoryItem, Param="FoundItems", Value=self.ItemName)
            pass

        source.addTask("TaskNotify", ID=Notificator.onItemClickToInventory,
                       Args=(self.Inventory, self.ItemName, self.EffectPolicy))
        source.addTask("TaskInventoryFXAddItem", InventoryItem=InventoryItem, ItemName=self.ItemName)
        source.addFunction(self.Inventory.UnBlockButtons)
