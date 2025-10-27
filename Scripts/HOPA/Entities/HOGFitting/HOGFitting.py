from Foundation.DemonManager import DemonManager
from HOPA.HOGFittingInventoryManager import HOGFittingInventoryManager


Enigma = Mengine.importEntity("Enigma")


class HOGFitting(Enigma):

    @staticmethod
    def declareORM(Type):
        Enigma.declareORM(Type)

        Type.addActionActivate("PrepareItems", Append=HOGFitting._appendPrepareItems)
        Type.addActionActivate("Items", Append=HOGFitting._appendItems, Remove=HOGFitting._removeItems)
        Type.addActionActivate("QueueItems", Append=HOGFitting._appendQueueItems)

    def __init__(self):
        super(HOGFitting, self).__init__()
        self.isHOG = True
        self.Inventory = None

    def _onPreparation(self):
        super(HOGFitting, self)._onPreparation()
        if self.isPlay() is True:
            self.__loadInventory()

    def _onDeactivate(self):
        super(HOGFitting, self)._onDeactivate()
        if self.Inventory is not None:
            self.Inventory.setParam("SlotFittingItemList", [])
            self.Inventory.setParam("SlotFittingItemListUsed", [])
            self.Inventory.setParam("ItemList", [])
            self.Inventory.setParam("SlotItems", [])
            self.Inventory.setParam("SlotIsFitting", [])

    def _onActivate(self):
        super(HOGFitting, self)._onActivate()
        if self.isPlay() is True:
            self.__loadParams()

    def _playEnigma(self):
        self.__loadInventory()
        self.__loadParams()

    def __loadParams(self):
        self.__updatePrepareItems(self.PrepareItems)
        self.__updateItems(self.Items)
        self.__updateQueueItems(self.QueueItems)

    def __loadInventory(self):
        if HOGFittingInventoryManager.hasInventory(self.EnigmaName) is True:
            self.Inventory = HOGFittingInventoryManager.getInventory(self.EnigmaName)
        else:
            self.Inventory = DemonManager.getDemon("HOGInventoryFitting")

    # //////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    def getInventory(self):
        return self.Inventory

    def __updatePrepareItems(self, list):
        if len(list) == 0:
            return

        SlotFittingItemList = self.Inventory.getSlotFittingItemList()
        for name in list:
            if name in SlotFittingItemList:
                continue
            self.Inventory.appendParam("SlotFittingItemList", name)

    def __updateItems(self, list):
        if len(list) == 0:
            return

        for name in list:
            self.__addItem(name)

    # param PrepareItems ///////////////////////////////////////////////////////////////////////////////////////////////

    def _appendPrepareItems(self, id, name):
        self.Inventory.appendParam("SlotFittingItemList", name)

    # param Items //////////////////////////////////////////////////////////////////////////////////////////////////////

    def _appendItems(self, id, name):
        self.__addItem(name)

    def __addItem(self, name):
        self.Inventory.appendParam("ItemList", name)

    def _removeItems(self, id, name, oldElements):
        if name in self.PrepareItems:
            self.object.delParam("PrepareItems", name)
        self.Inventory.appendParam("SlotFittingItemListUsed", name)
        self.__addQueueItem()

    # param QueueItems /////////////////////////////////////////////////////////////////////////////////////////////////

    def __updateQueueItems(self, QueueItems):
        for name in QueueItems:
            self.__addQueueItem()

    def _appendQueueItems(self, id, name):
        if self.Inventory.hasFreeSlot() is True:
            self.object.appendParam("PrepareItems", name)
            self.object.appendParam("Items", name)

            # item 100% in QueueItems, coz that method calls after QueueItems.append(name)
            self.QueueItems.remove(name)

    def __addQueueItem(self):
        queue = self.QueueItems
        if queue is None or len(queue) == 0:
            return False
        if self.Inventory.hasFreeSlot() is not True:
            return False

        item = queue[0]
        self.object.appendParam("PrepareItems", item)
        self.object.appendParam("Items", item)
        self.QueueItems.remove(item)
