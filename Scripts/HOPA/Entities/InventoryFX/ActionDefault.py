from Foundation.Initializer import Initializer
from Foundation.Task.TaskGenerator import TaskSource
from Foundation.TaskManager import TaskManager
from HOPA.ItemManager import ItemManager


class ActionDefault(Initializer):
    def __init__(self):
        super(ActionDefault, self).__init__()

        self.EndItem = False
        self.ItemName = None
        self.CurrentSlotIndex = None
        self._item_chain = None
        self._action_chain = None
        self._end_chain = None
        pass

    def _onFinalize(self):
        super(ActionDefault, self)._onFinalize()

        chain = self._end_chain
        self._end_chain = None
        if chain is not None:
            chain.cancel()

        chain = self._action_chain
        self._action_chain = None
        if chain is not None:
            chain.cancel()

        chain = self._item_chain
        self._item_chain = None
        if chain is not None:
            chain.cancel()

        self.Inventory = None
        self.InventoryItem = None

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

        self._runItemScope()
        pass

    def _runItemScope(self):
        tasks = []
        source = TaskSource(tasks)
        self._onRun(source)
        if len(tasks) == 0:
            return

        self._item_chain = TaskManager.createTaskChain(Source=tasks, Cb=self.__onItemComplete)
        self._item_chain.run()

    def _onRun(self, source):
        pass

    def __onItemComplete(self, isSkip):
        self._item_chain = None
        self.endItem(isSkip)

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

        self._end_chain = TaskManager.createTaskChain(Cb=self.__onEndComplete)
        with self._end_chain as tc:
            if self.EndItem is False:
                tc.addListener(Notificator.onItemEffectEnd, Filter=__thisItem)
                pass
            tc.addNotify(Notificator.onInventoryFXActionEnd, self, self.Inventory, self.InventoryItem, self.ItemName)
            pass

        pass

    def __onEndComplete(self, isSkip):
        self._end_chain = None

    def onSkip(self):
        pass

    def _onSkip(self):
        pass

    def onAction(self):
        self._action_chain = TaskManager.createTaskChain(Group=self.Inventory, Cb=self.__onActionComplete)
        with self._action_chain as source:
            self._onAction(source)
        pass

    def _onAction(self, source):
        source.addTask("AliasInventorySlotsMoveAddItem", Inventory=self.Inventory, InventoryItem=self.InventoryItem,
                       CurrentSlotIndex=self.CurrentSlotIndex)

    def __onActionComplete(self, isSkip):
        self._action_chain = None
        if self.isInitialized() is False:
            return

        self.checkEndItem(isSkip)

    def onEnd(self):
        self._onEnd()
        pass

    def _onEnd(self):
        pass

    pass
