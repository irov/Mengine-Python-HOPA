from HOPA.Entities.InventoryFX.ActionDefault import ActionDefault


class ActionDefaultRemove(ActionDefault):
    def onValues(self, *args):
        self.Inventory = args[0]
        self.InventoryItem = args[1]
        self.notifyOk = False

    def onRun(self):
        self._runItemScope()

    def checkEndItem(self, isSkip):
        Notification.notify(Notificator.onInventoryFXActionEnd, self, self.Inventory, self.InventoryItem, self.ItemName)
        self.notifyOk = True

    def _onAction(self, source):
        source.addTask("AliasInventorySlotsMoveRemoveItem", Inventory=self.Inventory, InventoryItem=self.InventoryItem)

    def _onEnd(self):
        if self.notifyOk is False:
            Notification.notify(Notificator.onInventoryFXActionEnd, self, self.Inventory, self.InventoryItem, self.ItemName)
            self.notifyOk = True
