import Foundation.Utils as Utils
from Foundation.DefaultManager import DefaultManager
from Foundation.TaskManager import TaskManager
from HOPA.HOGManager import HOGManager
from Notification import Notification


Enigma = Mengine.importEntity("Enigma")


class HOGSilhouette(Enigma):
    @staticmethod
    def declareORM(Type):
        Enigma.declareORM(Type)
        Type.addAction(Type, "FoundItems")
        Type.addAction(Type, "FindItems")
        pass

    def __init__(self):
        super(HOGSilhouette, self).__init__()

        self.ItemsGroup = None
        self.HOGInventory = None
        self.tempItems = []
        self.completeCheck = False
        self.isHOG = True
        pass

    def _onActivate(self):
        super(HOGSilhouette, self)._onActivate()
        HOGItemsInDemon = DefaultManager.getDefaultBool("HOGItemsInDemon", True)

        if HOGItemsInDemon is True:
            self.ItemsGroup = self.object
            return
            pass

        self.ItemsGroup = self.object.getGroup()
        pass

    def _restoreEnigma(self):
        self.HOGItems = HOGManager.getHOGItems(self.EnigmaName)

        self.HOGInventory = HOGManager.getInventory(self.EnigmaName)
        self.HOGInventory.setEnable(True)

        self._findItems()

    def _playEnigma(self):
        self.HOGInventory = HOGManager.getInventory(self.EnigmaName)
        self.HOGInventory.setEnable(True)

        self.HOGItems = HOGManager.getHOGItems(self.EnigmaName)

        for hogItem in self.HOGItems:
            itemObjectName = hogItem.objectName
            if itemObjectName not in self.FoundItems:
                continue

            item = self.ItemsGroup.getObject(itemObjectName)
            if item.getEnable() is False:
                continue

            item.setEnable(False)

        countItems = self.HOGInventory.getSlotCount()

        FindItems = self._findNewInventoryItems(countItems)

        self.object.setFindItems(FindItems)

        self._findItems()

        pass

    def _findItems(self):
        self.HOGInventory.setParams(HOG=self.object)

        for id, item in enumerate(self.FindItems):
            self._findItem(item, id)

        if len(self.FoundItems) != 0:
            for itemName in self.FoundItems[:]:
                self.HOGInventory.appendParam("FoundItems", itemName)

    def _findItem(self, itemName, id):
        self.HOGInventory.appendParam("FindItems", itemName)

        hogItem = HOGManager.getHOGItem(self.EnigmaName, itemName)

        if hogItem.objectName is None:
            return

        with TaskManager.createTaskChain(Name="HOGFindItem{}".format(itemName), Group=self.ItemsGroup,
                                         Cb=self._changeSlotItem, CbArgs=(itemName, id)) as tc:
            tc.addTask("AliasHOGSilhouetteFindItem", HOG=self.object, HOGItemName=itemName, EnigmaName=self.EnigmaName)

    def _changeSlotItem(self, isSkip, itemName, id):
        if self.object.getPlay() is False:
            return

        if itemName in self.FindItems:
            self.object.delParam("FindItems", itemName)
            self.HOGInventory.delParam("FindItems", itemName)

        if self.checkComplete() is True:
            return

        itemList = self._findNewInventoryItems(1)

        if len(itemList) == 0:
            return

        nextItem = itemList[0]

        self.object.appendParam("FindItems", nextItem)

        if isSkip is False:
            self._findItem(nextItem, id)

    def checkComplete(self):
        if len(self.HOGItems) == len(self.FoundItems):
            self._onHOGComplete()
            self.tempItems = self.HOGItems
            self.completeCheck = True

            return True

        return False

    def _onHOGComplete(self):
        self.object.setParam("FoundItems", [])
        self.object.setParam("FindItems", [])

        self.enigmaComplete()
        Notification.notify(Notificator.onHOGComplete, self.object)

        return False

    def _findNewInventoryItems(self, count):
        AllFindItems = []
        inventoryFindItems = self.HOGInventory.getFindItems()

        for hogItem in self.HOGItems:
            if hogItem.itemName in self.FoundItems:
                continue

            AllFindItems.append(hogItem.itemName)

            for inventoryItemName in inventoryFindItems:
                if hogItem.itemName == inventoryItemName:
                    AllFindItems.remove(hogItem.itemName)
                    break

        newFindItems = Utils.rand_sample_list(AllFindItems, min(count, len(AllFindItems)))

        return newFindItems

    def _enableSceneHogItem(self):
        HOGItemsEnableAfterComplete = DefaultManager.getDefaultBool("HOGItemsEnableAfterComplete", False)
        if HOGItemsEnableAfterComplete is True:
            for hogItem in self.tempItems:
                itemObjectName = hogItem.objectName

                if itemObjectName is None:
                    continue
                    pass

                item = self.ItemsGroup.getObject(itemObjectName)
                item.setEnable(True)
                pass
            pass

    def _stopEnigma(self):
        self.HOGInventory.setParams(FindItems=[], FoundItems=[], HOG=None)

        Notification.notify(Notificator.onHOGStop, self.object)

    def _skipEnigma(self):
        if self.object.getPlay() is True:
            self.enigmaComplete()

        Notification.notify(Notificator.onHOGSkip, self.object)

    def _onDeactivate(self):
        super(HOGSilhouette, self)._onDeactivate()

        for itemName in self.FindItems[:]:
            if TaskManager.existTaskChain("HOGFindItem{}".format(itemName)) is True:
                TaskManager.cancelTaskChain("HOGFindItem{}".format(itemName))

        self.HOGInventory.setParams(FindItems=[], FoundItems=[], HOG=None)

        if self.completeCheck is True:
            self._enableSceneHogItem()

        self.completeCheck = False
        self.tempItems = []
        pass

    pass
