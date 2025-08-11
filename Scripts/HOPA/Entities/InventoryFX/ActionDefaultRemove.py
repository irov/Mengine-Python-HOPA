from Foundation.Initializer import Initializer
from Foundation.TaskManager import TaskManager

class ActionDefaultRemove(Initializer):
    def __init__(self):
        super(ActionDefaultRemove, self).__init__()

        self.EndItem = False
        self.ItemName = None
        self.CurrentSlotIndex = None

    def onValues(self, *args):
        self.Inventory = args[0]
        self.InventoryItem = args[1]
        self.notifyOk = False

    def setItemName(self, name):
        self.ItemName = name

    def getItemName(self):
        return self.ItemName

    def setType(self, actionType):
        self.actionType = actionType

    def getType(self):
        return self.actionType

    def onCheck(self):
        return self._onCheck()

    def _onCheck(self):
        return True

    def onRun(self):
        self._onRun()

    def _onRun(self):
        pass

    def endItem(self, isSkip):
        self.EndItem = True

    def checkEndItem(self, isSkip):
        Notification.notify(Notificator.onInventoryFXActionEnd, self, self.Inventory, self.InventoryItem, self.ItemName)
        self.notifyOk = True

    def onSkip(self):
        pass

    def _onSkip(self):
        pass

    def onAction(self):
        self._onAction()
        pass

    def _onAction(self):
        with TaskManager.createTaskChain(Name="InvFXActionDefaultRemove", Group=self.Inventory, Cb=self.checkEndItem) as tc:
            tc.addTask("AliasInventorySlotsMoveRemoveItem", Inventory=self.Inventory, InventoryItem=self.InventoryItem)

    def onEnd(self):
        self._onEnd()

    def _onEnd(self):
        if self.notifyOk is False:
            Notification.notify(Notificator.onInventoryFXActionEnd, self, self.Inventory, self.InventoryItem, self.ItemName)
            self.notifyOk = True
