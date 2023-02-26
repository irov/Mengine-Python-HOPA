from Foundation.DefaultManager import DefaultManager
from Foundation.PolicyManager import PolicyManager
from Foundation.TaskManager import TaskManager
from HOPA.EnigmaManager import EnigmaManager
from HOPA.HOGManager import HOGManager
from Notification import Notification

Enigma = Mengine.importEntity("Enigma")

class HOG(Enigma):

    @staticmethod
    def declareORM(Type):
        Enigma.declareORM(Type)

        Type.addAction(Type, "FoundItems")
        pass

    def __init__(self):
        super(HOG, self).__init__()

        self.ItemsGroup = None
        self.isHOG = True
        self.isMiniHOG = True
        pass

    def _skipEnigma(self):
        if TaskManager.existTaskChain("HOGFindItem") is True:
            TaskManager.cancelTaskChain("HOGFindItem")
            pass

        Notification.notify(Notificator.onHOGSkip, self.object)

        self._onHOGComplete()
        pass

    def _enableSceneHogItems(self):
        HOGItemsEnableAfterComplete = DefaultManager.getDefaultBool("HOGItemsEnableAfterComplete", False)
        if HOGItemsEnableAfterComplete is True:
            sceneName = EnigmaManager.getEnigmaSceneName(self.EnigmaName)

            HOGItems = HOGManager.getSceneHOGItems(self.EnigmaName, sceneName)
            for hogItem in HOGItems:
                itemObjectName = hogItem.objectName

                if itemObjectName is None:
                    continue
                    pass

                item = self.ItemsGroup.getObject(itemObjectName)
                item.setEnable(True)
                pass
            pass
        pass

    def _playEnigma(self):
        HOGItemsInDemon = DefaultManager.getDefaultBool("HOGItemsInDemon", True)

        if HOGItemsInDemon is True:
            self.ItemsGroup = self.object
            pass
        else:
            self.ItemsGroup = self.object.getGroup()
            pass

        HOGItems = HOGManager.getHOGItems(self.EnigmaName)

        if self.checkComplete(False) is True:
            return
            pass

        for hogItem in HOGItems:
            if hogItem.itemName not in self.FoundItems:
                continue
                pass

            if hogItem.objectName is None:
                continue
                pass

            item = self.ItemsGroup.getObject(hogItem.objectName)

            if item.getEnable() is False:
                continue
                pass

            item.setEnable(False)
            pass

        FindItems = []
        for hogItem in HOGItems:
            if hogItem.itemName in self.FoundItems:
                continue
                pass

            FindItems.append(hogItem.itemName)
            pass

        if len(FindItems) == 0:
            Trace.log("Entity", 0, "HOG %s find items empty" % (self.object.name))
            return
            pass

        self.HOGInventory = HOGManager.getInventory(self.EnigmaName)
        self.HOGInventory.setParams(HOGName=self.EnigmaName, HOGItems=[hogItem.itemName for hogItem in HOGItems[:]], FoundItems=self.FoundItems[:])

        policy = PolicyManager.getPolicy("HOGFindItem", "AliasHOGFindItem")

        with TaskManager.createTaskChain(Name="HOGFindItem", Group=self.ItemsGroup, Cb=self.checkComplete) as tc:
            itemCount = len(FindItems)
            with tc.addParallelTask(itemCount) as tcho:
                for tc_hog, name in zip(tcho, FindItems):
                    hogItem = HOGManager.getHOGItem(self.EnigmaName, name)
                    if hogItem.objectName is None:
                        continue
                        pass

                    tc_hog.addTask(policy, HOG=self.object, HOGItemName=name, EnigmaName=self.EnigmaName)
                    pass
                pass
            pass

        Notification.notify(Notificator.onHOGStart, self.object)
        pass

    def _stopEnigma(self):
        self.HOGInventory.setParams(HOGName=None, HOGItems=None, FoundItems=[])

        if TaskManager.existTaskChain("HOGFindItem") is True:
            TaskManager.cancelTaskChain("HOGFindItem")
            pass

        Notification.notify(Notificator.onHOGStop, self.object)
        pass

    def checkComplete(self, isSkip):
        HOGItems = HOGManager.getHOGItems(self.EnigmaName)

        if len(HOGItems) != len(self.FoundItems):
            return False
            pass

        self._onHOGComplete()

        TaskManager.runAlias("TaskFadeIn", None, GroupName="Fade")
        self._enableSceneHogItems()

        return True
        pass

    def _onHOGComplete(self):
        self.object.setParam("Play", False)
        self.object.setParam("FoundItems", [])

        self.HOGInventory.setParams(HOGName=None, HOGItems=None, FoundItems=[])

        # HOGItemsEnableAfterComplete = DefaultManager.getDefaultBool("HOGItemsEnableAfterComplete", False)
        # if HOGItemsEnableAfterComplete is True:
        #     HOGItems = HOGManager.getHOGItems(self.EnigmaName)
        #     for hogItem in HOGItems:
        #         itemObjectName = hogItem.objectName
        #
        #         if itemObjectName is None:
        #             continue
        #             pass
        #
        #         item = self.ItemsGroup.getObject(itemObjectName)
        #         item.setEnable(True)
        #         pass
        #     pass

        Notification.notify(Notificator.onHOGComplete, self.object)

        self.enigmaComplete()
        pass

    pass