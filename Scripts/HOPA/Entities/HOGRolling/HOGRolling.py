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
        Type.addAction(Type, "FoundItems")  # , Update = HOGRolling._test_Print, Append = HOGRolling._test_Print)
        Type.addAction(Type, "FindItems")
        pass

    def __init__(self):
        super(HOGRolling, self).__init__()

        self.ItemsGroup = None
        self.HOGInventory = None
        self.tempItems = []
        self.completeCheck = False
        self.isHOG = True

        pass

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
            pass

        self.ItemsGroup = self.object.getGroup()
        pass

    def _playEnigma(self):
        self.HOGInventory.setEnable(True)

        if self.checkComplete() is True:
            return
            pass

        for hogItem in self.HOGItems:
            itemObjectName = hogItem.objectName
            if itemObjectName not in self.FoundItems:
                continue
                pass

            item = self.ItemsGroup.getObject(itemObjectName)

            if item.getEnable() is False:
                continue
                pass

            item.setEnable(False)
            pass

        countItems = self.HOGInventory.getSlotCount()
        FindItems = self._findNewInventoryItems(countItems)
        self.object.setFindItems(FindItems)

        self._findItems()

        Notification.notify(Notificator.onHOGStart, self.object)
        pass

    def _restoreEnigma(self):
        self.HOGItems = HOGManager.getHOGItems(self.EnigmaName)

        self.HOGInventory = HOGManager.getInventory(self.EnigmaName)
        self.HOGInventory.setEnable(True)

        self._findItems()
        pass

    def _findItems(self):
        self.HOGInventory.setParams(HOG=self.object)

        for id, itemList in enumerate(self.FindItems):
            self._findItem(itemList, id)
            pass

        if len(self.FoundItems) != 0:
            for hogItemName in self.FoundItems[:]:
                self.HOGInventory.appendParam("FoundItems", hogItemName)
                pass
            pass

        self.HOGInventory.setItemsCount(len(self.HOGItems))
        pass

    def _findNewInventoryItems(self, count):
        AllFindItems = []
        inventoryFindItems = self.HOGInventory.getFindItems()

        for hogItem in self.HOGItems:
            if hogItem.itemName in self.FoundItems:
                continue
                pass

            AllFindItems.append(hogItem.itemName)

            for slotItems in inventoryFindItems:
                for inventoryItemName in slotItems:
                    if hogItem.itemName == inventoryItemName:
                        AllFindItems.remove(hogItem.itemName)
                        break
                        pass
                    pass
                pass
            pass

        filterItems = HOGManager.filterCountItems(AllFindItems, self.EnigmaName)

        newFindItems = Utils.rand_sample_list(filterItems, min(count, len(filterItems)))

        return newFindItems
        pass

    def _findItem(self, listNames, id):
        self.HOGInventory.appendParam("FindItems", listNames)

        for itemName in listNames:
            hogItem = HOGManager.getHOGItem(self.EnigmaName, itemName)
            if hogItem.objectName is None:
                return
                pass
            pass

        with TaskManager.createTaskChain(Name="HOGFindItem%s" % listNames, Group=self.ItemsGroup, Cb=self.__changeSlotItem, CbArgs=(listNames, id)) as tc:
            itemCount = len(listNames)
            with tc.addParallelTask(itemCount) as tcho:
                for tc_hog, name in zip(tcho, listNames):
                    if name not in self.FoundItems:
                        tc_hog.addTask("AliasHOGRollingFindItem", HOG=self.object, HOGItemName=name, EnigmaName=self.EnigmaName)
                        # with tc_hog.addParallelTask(2) as (tc_hog_1, tc_hog_2):
                        #     tc_hog_1.addFunction(disableMovie, name)
                        #     tc_hog_2.addFunction(enableItem, name)
                        pass
                    else:
                        tc_hog.addTask("TaskDummy")
                        pass

                    pass
                pass
            pass
        pass

    def __changeSlotItem(self, isSkip, listNames, id):
        if self.object.getPlay() is False:
            return
            pass

        if listNames in self.FindItems:
            self.object.delParam("FindItems", listNames)
            self.HOGInventory.delParam("FindItems", listNames)
            pass

        if self.checkComplete() is True:
            return
            pass

        itemList = self._findNewInventoryItems(1)

        if len(itemList) == 0:
            return
            pass

        nextList = itemList[0]

        self.object.appendParam("FindItems", nextList)

        if isSkip is False:
            self._findItem(nextList, id)
            pass
        pass

    def _enableSceneHogItems(self):
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
        pass

    def checkComplete(self):
        if len(self.HOGItems) == len(self.FoundItems):
            self.tempItems = self.HOGItems
            self.completeCheck = True
            # self._enableSceneHogItems()
            self._onHOGComplete()

            return True
            pass

        return False
        pass

    def _onHOGComplete(self):
        self.object.setParam("FoundItems", [])
        self.object.setParam("FindItems", [])

        Notification.notify(Notificator.onHOGComplete, self.object)

        self.enigmaComplete()

        return False
        pass

    def _skipEnigma(self):
        if self.object.getPlay() is True:
            self.enigmaComplete()
            pass

        Notification.notify(Notificator.onHOGSkip, self.object)
        pass

    def _stopEnigma(self):
        self.HOGInventory.setParams(FindItems=[], FoundItems=[], HOG=None)

        Notification.notify(Notificator.onHOGStop, self.object)
        pass

    def _pauseEnigma(self):
        pass

    def _onDeactivate(self):
        super(HOGRolling, self)._onDeactivate()
        for listNames in self.FindItems[:]:
            if TaskManager.existTaskChain("HOGFindItem%s" % listNames) is True:
                TaskManager.cancelTaskChain("HOGFindItem%s" % listNames)
                pass
            pass

        if self.HOGInventory is not None:
            self.HOGInventory.setParams(FindItems=[], FoundItems=[], HOG=None)
        else:
            Trace.log("Entity", 0, "HOG Rolling '{}' hog inventory is None".format(self.getName()))
            pass

        if self.completeCheck is True:
            self._enableSceneHogItems()
            pass

        self.completeCheck = False
        self.tempItems = []
        pass
    pass