from Foundation.Initializer import Initializer
from Foundation.TaskManager import TaskManager
from Notification import Notification

class ActionDefaultRemove(Initializer):
    def __init__(self):
        super(ActionDefaultRemove, self).__init__()

        self.EndItem = False
        self.ItemName = None
        self.CurrentSlotIndex = None
        pass

    def onValues(self, *args):
        self.Inventory = args[0]
        self.InventoryItem = args[1]
        self.notifyOk = False
        pass

    def setItemName(self, name):
        self.ItemName = name
        pass

    def getItemName(self):
        return self.ItemName
        pass

    def setType(self, actionType):
        self.actionType = actionType
        pass

    def getType(self):
        return self.actionType
        pass

    def onCheck(self):
        return self._onCheck()
        pass

    def _onCheck(self):
        return True
        pass

    def onRun(self):
        self._onRun()
        pass

    def _onRun(self):
        pass

    def endItem(self, isSkip):
        self.EndItem = True
        pass

    def checkEndItem(self, isSkip):
        Notification.notify(Notificator.onInventoryFXActionEnd, self, self.Inventory, self.InventoryItem, self.ItemName)
        self.notifyOk = True
        pass

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
            pass
        pass

    def onEnd(self):
        self._onEnd()
        pass

    def _onEnd(self):
        if self.notifyOk is False:
            Notification.notify(Notificator.onInventoryFXActionEnd, self, self.Inventory, self.InventoryItem, self.ItemName)
            self.notifyOk = True
            pass
        pass

    pass