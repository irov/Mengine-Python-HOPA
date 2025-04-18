from Foundation.ArrowManager import ArrowManager
from Foundation.Task.TaskAlias import TaskAlias


class AliasInventoryRemoveInventoryItemFX(TaskAlias):
    def _onParams(self, params):
        super(AliasInventoryRemoveInventoryItemFX, self)._onParams(params)

        self.InventoryItem = params.get("InventoryItem")
        self.Inventory = params.get("Inventory")

    def _onGenerate(self, source):
        if ArrowManager.emptyArrowAttach() is False:
            Attach = ArrowManager.getArrowAttach()
            if Attach is self.InventoryItem:
                source.addTask("TaskRemoveArrowAttach")

        InventoryItems = self.Inventory.getParam("InventoryItems")

        if self.InventoryItem not in InventoryItems:
            Trace.log("Notification", 0, "AliasInventoryRemoveInventoryItemFX._onGenerate Inventory %s not have InventoryItem %s" % (self.Inventory.getName(), self.InventoryItem.getName()))
            return

        source.addNotify(Notificator.onInventoryClickRemoveItem, self.Inventory, self.InventoryItem, "ActionRemoveItem")

        source.addTask("TaskObjectReturn", Object=self.InventoryItem)
        source.addDisable(self.InventoryItem)

        source.addNotify(Notificator.onInventoryRemoveInventoryItem, self.Inventory, self.Inventory)
