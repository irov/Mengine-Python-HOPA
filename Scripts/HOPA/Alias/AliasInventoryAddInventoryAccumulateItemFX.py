from Foundation.ArrowManager import ArrowManager
from Foundation.Task.TaskAlias import TaskAlias
from HOPA.ItemManager import ItemManager

class AliasInventoryAddInventoryAccumulateItemFX(TaskAlias):
    def _onParams(self, params):
        super(AliasInventoryAddInventoryAccumulateItemFX, self)._onParams(params)

        self.Inventory = params.get("Inventory")
        self.ItemName = params.get("ItemName")
        self.EffectPolicy = params.get("EffectPolicy")
        self.Value = params.get("Value")
        pass

    def _onGenerate(self, source):
        source.addFunction(self.Inventory.BlockButtons)

        def setValue(value):
            old = InventoryItem.getValue()
            new = old + value
            InventoryItem.setValue(new)
            pass

        InventoryItem = ItemManager.getItemInventoryItem(self.ItemName)
        InventoryItemEntity = InventoryItem.getEntity()

        if ArrowManager.emptyArrowAttach() is False:
            source.addTask("AliasInventoryReturnInventoryItemFX", Inventory=self.Inventory)
            pass

        hasInventoryItem = self.Inventory.hasInventoryItem(InventoryItem)

        if hasInventoryItem is False:
            source.addTask("TaskInventoryAddItem", Inventory=self.Inventory, ItemName=self.ItemName)
            source.addTask("TaskInventorySlotAddInventoryItem", Inventory=self.Inventory, InventoryItem=InventoryItem)
            source.addTask("TaskNodeEnable", Node=InventoryItemEntity, Value=False)
            pass

        source.addTask("TaskFunction", Fn=setValue, Args=(self.Value,))

        source.addTask("TaskNotify", ID=Notificator.onItemClickToInventory, Args=(self.Inventory, self.ItemName, "ActionPickItem"))
        source.addFunction(self.Inventory.UnBlockButtons)
        pass

    pass