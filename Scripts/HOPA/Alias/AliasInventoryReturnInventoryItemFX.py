from Foundation.ArrowManager import ArrowManager
from Foundation.Task.TaskAlias import TaskAlias


class AliasInventoryReturnInventoryItemFX(TaskAlias):
    def _onParams(self, params):
        super(AliasInventoryReturnInventoryItemFX, self)._onParams(params)

        self.Inventory = params.get("Inventory")
        self.UnblockInventory = params.get("UnblockInventory", False)
        self.Return = params.get("Return", True)

    def _onInitialize(self):
        super(AliasInventoryReturnInventoryItemFX, self)._onInitialize()

        if _DEVELOPMENT is True:
            if ArrowManager.emptyArrowAttach() is True:
                self.initializeFailed("AliasInventoryReturnInventoryItemFX Attach not found")

    def _onGenerate(self, source):
        InventoryItem = ArrowManager.getArrowAttach()

        InventoryItems = self.Inventory.getParam("InventoryItems")
        if InventoryItem not in InventoryItems:
            InventoryItem.setEnable(False)
            return
            pass

        InventoryItemEntity = InventoryItem.getEntity()
        InventoryItemEntityNode = InventoryItem.getEntityNode()
        pos = InventoryItemEntity.getWorldPosition()
        state = InventoryItemEntity.getState()
        if state == InventoryItemEntity.ITEM_TAKE:
            return
            pass

        source.addNotify(Notificator.onInventoryClickReturnItem, self.Inventory, InventoryItem)

        source.addTask("TaskRemoveArrowAttach")

        if self.Return is True:
            InventoryItems = self.Inventory.getParam("InventoryItems")

            InventoryItemReturnIndex = InventoryItems.index(InventoryItem)
            CurrentSlotIndex = self.Inventory.getCurrentSlotIndex()

            SetSlotIndex = InventoryItemReturnIndex - CurrentSlotIndex

            source.addTask("TaskSceneLayerAddEntity", LayerName="InventoryItemEffect",
                           Object=InventoryItem, AdaptScreen=True)
            source.addTask("TaskNodeSetPosition", Node=InventoryItemEntityNode, Value=pos)

            source.addTask("AliasEffectInventoryReturnInventoryItem", Inventory=self.Inventory,
                           SlotID=SetSlotIndex, InventoryItem=InventoryItem)

            # source.addTask("TaskObjectReturn", Object = InventoryItem)

            source.addNotify(Notificator.onInventoryReturnInventoryItem, self.Inventory, InventoryItem)
            source.addTask("TaskInventorySlotReturnItemFX", Inventory=self.Inventory, InventoryItem=InventoryItem)

        if self.UnblockInventory is True:
            source.addTask("TaskInventoryDetachItem", Inventory=self.Inventory, InventoryItem=InventoryItem)
