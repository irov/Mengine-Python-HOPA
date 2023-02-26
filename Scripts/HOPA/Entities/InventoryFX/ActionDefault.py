from Foundation.Initializer import Initializer
from Foundation.TaskManager import TaskManager
from HOPA.ItemManager import ItemManager

class ActionDefault(Initializer):
    def __init__(self):
        super(ActionDefault, self).__init__()

        self.EndItem = False
        self.ItemName = None
        self.CurrentSlotIndex = None
        pass

    def onValues(self, *args):
        self.Inventory = args[1]
        self.ItemName = args[2]
        self.InventoryItem = ItemManager.getItemInventoryItem(self.ItemName)
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
        CountRight = self.Inventory.getScrollCountRight(self.InventoryItem)
        CountLeft = self.Inventory.getScrollCountLeft(self.InventoryItem)
        if CountRight >= 1:
            self.CurrentSlotIndex = None
            pass
        elif CountLeft >= 1:
            self.CurrentSlotIndex = None
            pass
        else:
            self.CurrentSlotIndex = self.Inventory.getCurrentSlotIndex()
            pass

        self._onRun()
        pass

    def _onRun(self):
        pass

    def endItem(self, isSkip):
        self.EndItem = True
        pass

    def checkEndItem(self, isSkip):
        def __thisItem(itemName):
            if itemName != self.ItemName:
                return False
                pass

            self.InventoryItem.setEnable(True)
            return True
            pass

        with TaskManager.createTaskChain() as tc:
            if self.EndItem is False:
                tc.addTask("TaskListener", ID=Notificator.onItemEffectEnd, Filter=__thisItem)
                pass
            tc.addTask("TaskNotify", ID=Notificator.onInventoryFXActionEnd, Args=(self, self.Inventory, self.InventoryItem, self.ItemName))
            pass

        pass

    def onSkip(self):
        # self._onSkip()
        #
        # if TaskManager.existTaskChain("InvFXActionDefault"):
        #     TaskManager.cancelTaskChain("InvFXActionDefault")
        #     pass
        pass

    def _onSkip(self):
        pass

    def onAction(self):
        self._onAction()
        pass

    def _onAction(self):
        with TaskManager.createTaskChain(Name="InvFXActionDefault", Group=self.Inventory, Cb=self.checkEndItem) as tc:
            tc.addTask("AliasInventorySlotsMoveAddItem", Inventory=self.Inventory, InventoryItem=self.InventoryItem, CurrentSlotIndex=self.CurrentSlotIndex)
            pass
        pass

    def onEnd(self):
        self._onEnd()
        pass

    def _onEnd(self):
        pass

    pass