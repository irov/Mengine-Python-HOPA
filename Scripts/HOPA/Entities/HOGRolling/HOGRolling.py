import Foundation.Utils as Utils
from Foundation.DefaultManager import DefaultManager
from Foundation.TaskManager import TaskManager
from HOPA.HOGManager import HOGManager
from Notification import Notification


Enigma = Mengine.importEntity("Enigma")


class HOGRolling(Enigma):

    @staticmethod
    def declareORM(Type):
        Enigma.declareORM(Type)
        Type.addAction(Type, "FoundItems")
        Type.addAction(Type, "FindItems")

    def __init__(self):
        super(HOGRolling, self).__init__()

        self.ItemsGroup = None
        self.HOGInventory = None
        self.tempItems = []
        self.completeCheck = False
        self.isHOG = True

    def _onPreparation(self):
        super(HOGRolling, self)._onPreparation()
        self.HOGItems = HOGManager.getHOGItems(self.EnigmaName)

        self.HOGInventory = HOGManager.getInventory(self.EnigmaName)
        if self.HOGInventory is None:
            Trace.log("Entity", 0, "HOG Rolling '{}' hog inventory is None".format(self.getName()))

    def _onActivate(self):
        super(HOGRolling, self)._onActivate()
        HOGItemsInDemon = DefaultManager.getDefaultBool("HOGItemsInDemon", True)

        if HOGItemsInDemon is True:
            self.ItemsGroup = self.object
            return

        self.ItemsGroup = self.object.getGroup()

    def _playEnigma(self):
        self.HOGInventory.setEnable(True)

        if self.checkComplete() is True:
            return

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

        Notification.notify(Notificator.onHOGStart, self.object)

    def _restoreEnigma(self):
        self.HOGItems = HOGManager.getHOGItems(self.EnigmaName)

        self.HOGInventory = HOGManager.getInventory(self.EnigmaName)
        self.HOGInventory.setEnable(True)

        self._findItems()

    def _findItems(self):
        self.HOGInventory.setParams(HOG=self.object)

        for id, itemList in enumerate(self.FindItems):
            self._findItem(itemList, id)

        if len(self.FoundItems) != 0:
            for hogItemName in self.FoundItems[:]:
                self.HOGInventory.appendParam("FoundItems", hogItemName)

        self.HOGInventory.setItemsCount(len(self.HOGItems))

    def _findNewInventoryItems(self, count):
        AllFindItems = []
        inventoryFindItems = self.HOGInventory.getFindItems()

        for hogItem in self.HOGItems:
            if hogItem.itemName in self.FoundItems:
                continue

            AllFindItems.append(hogItem.itemName)

            for slotItems in inventoryFindItems:
                for inventoryItemName in slotItems:
                    if hogItem.itemName == inventoryItemName:
                        AllFindItems.remove(hogItem.itemName)
                        break

        filterItems = HOGManager.filterCountItems(AllFindItems, self.EnigmaName)

        newFindItems = Utils.rand_sample_list(filterItems, min(count, len(filterItems)))

        return newFindItems

    def _findItem(self, listNames, id):
        self.HOGInventory.appendParam("FindItems", listNames)

        for itemName in listNames:
            hogItem = HOGManager.getHOGItem(self.EnigmaName, itemName)
            if hogItem.objectName is None:
                return

        with TaskManager.createTaskChain(Name="HOGFindItem%s" % listNames, Group=self.ItemsGroup,
                                         Cb=self.__changeSlotItem, CbArgs=(listNames, id)) as tc:
            itemCount = len(listNames)
            with tc.addParallelTask(itemCount) as tcho:
                for tc_hog, name in zip(tcho, listNames):
                    if name not in self.FoundItems:
                        tc_hog.addTask("AliasHOGRollingFindItem", HOG=self.object, HOGItemName=name,
                                       EnigmaName=self.EnigmaName)
                        # with tc_hog.addParallelTask(2) as (tc_hog_1, tc_hog_2):
                        #     tc_hog_1.addFunction(disableMovie, name)
                        #     tc_hog_2.addFunction(enableItem, name)
                    else:
                        tc_hog.addTask("TaskDummy")

    def __changeSlotItem(self, isSkip, listNames, id):
        if self.object.getPlay() is False:
            return

        if listNames in self.FindItems:
            self.object.delParam("FindItems", listNames)
            self.HOGInventory.delParam("FindItems", listNames)

        if self.checkComplete() is True:
            return

        itemList = self._findNewInventoryItems(1)

        if len(itemList) == 0:
            return

        nextList = itemList[0]

        self.object.appendParam("FindItems", nextList)

        if isSkip is False:
            self._findItem(nextList, id)

    def _enableSceneHogItems(self):
        HOGItemsEnableAfterComplete = DefaultManager.getDefaultBool("HOGItemsEnableAfterComplete", False)
        if HOGItemsEnableAfterComplete is True:
            for hogItem in self.tempItems:
                itemObjectName = hogItem.objectName

                if itemObjectName is None:
                    continue

                item = self.ItemsGroup.getObject(itemObjectName)
                item.setEnable(True)

    def checkComplete(self):
        if len(self.HOGItems) == len(self.FoundItems):
            self.tempItems = self.HOGItems
            self.completeCheck = True
            # self._enableSceneHogItems()
            self._onHOGComplete()

            return True

        return False

    def _onHOGComplete(self):
        self.object.setParam("FoundItems", [])
        self.object.setParam("FindItems", [])

        Notification.notify(Notificator.onHOGComplete, self.object)

        self.enigmaComplete()

        return False

    def _skipEnigma(self):
        if self.object.getPlay() is True:
            self.enigmaComplete()

        Notification.notify(Notificator.onHOGSkip, self.object)

    def _stopEnigma(self):
        self.HOGInventory.setParams(FindItems=[], FoundItems=[], HOG=None)

        Notification.notify(Notificator.onHOGStop, self.object)

    def _pauseEnigma(self):
        pass

    def _onDeactivate(self):
        super(HOGRolling, self)._onDeactivate()
        for listNames in self.FindItems[:]:
            if TaskManager.existTaskChain("HOGFindItem%s" % listNames) is True:
                TaskManager.cancelTaskChain("HOGFindItem%s" % listNames)

        if self.HOGInventory is not None:
            self.HOGInventory.setParams(FindItems=[], FoundItems=[], HOG=None)
        else:
            Trace.log("Entity", 0, "HOG Rolling '{}' hog inventory is None".format(self.getName()))

        if self.completeCheck is True:
            self._enableSceneHogItems()

        self.completeCheck = False
        self.tempItems = []

