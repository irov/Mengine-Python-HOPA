from Foundation.ArrowManager import ArrowManager
from Foundation.Task.TaskAlias import TaskAlias


class AliasHOGFittingReturnItemToSlot(TaskAlias):
    def __init__(self):
        super(AliasHOGFittingReturnItemToSlot, self).__init__()
        pass

    def _onParams(self, params):
        super(AliasHOGFittingReturnItemToSlot, self)._onParams(params)
        self.Inventory = params.get("Inventory")
        pass

    def _onInitialize(self):
        super(AliasHOGFittingReturnItemToSlot, self)._onInitialize()
        pass

    def _onGenerate(self, source):
        if ArrowManager.getArrowAttach() is None:
            return

        invEnt = self.Inventory.getEntity()
        slot = invEnt.PickedItemSlot

        self.ItemName = slot.ItemName
        self.ItemObject = slot.ItemStore
        self.InventoryItemObject = slot.ItemHideStore

        def RemoveVisualFromAttach():
            Item = ArrowManager.getArrowAttach()
            ArrowManager.removeArrowAttach()
            Item.setEnable(False)
            pass

        source.addFunction(RemoveVisualFromAttach)
        source.addTask("AliasHOGFittingMoveItemToSlot", Inventory=self.Inventory, ItemName=self.ItemName,
                       ItemObject=self.ItemObject, InventoryItemObject=self.InventoryItemObject)

        def ReturnItem():
            invEnt.returnSlotItem(self.ItemName)

        source.addFunction(ReturnItem)
