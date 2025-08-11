from Foundation.Manager import Manager

from Foundation.DatabaseManager import DatabaseManager
from Foundation.GroupManager import GroupManager


class HOGImageManager(Manager):
    s_hogs = {}

    class HOGImage(object):
        def __init__(self, items):
            self.items = items

        def getItems(self):
            return self.items

    @staticmethod
    def _onFinalize():
        HOGImageManager.s_hogs = {}
        pass

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            Name = record.get("HOGName")
            Param = record.get("Param")

            hog = HOGImageManager.loadHOG(Name, Param)

            if hog is None:
                Trace.log("HOGManager", 0, "HOGImageManager.loadHOGs: invalid load hog %s" % (Name))
                return False

        return True

    @staticmethod
    def loadHOG(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)
        items = {}

        for record in records:
            HOGItemName = record.get("HOGItemName")
            GroupName = record.get("GroupName")
            ObjectName = record.get("ObjectName")

            object = GroupManager.getObject(GroupName, ObjectName)
            items[HOGItemName] = object
            pass

        hog = HOGImageManager.HOGImage(items)
        HOGImageManager.addHOG(module, hog)

        return hog

    @staticmethod
    def hasHOG(name):
        return name in HOGImageManager.s_hogs

    @staticmethod
    def getHOGInventoryImage(hogName, hogItemName):
        if HOGImageManager.hasHOG(hogName) is False:
            Trace.log("Manager", 0, "HOGImageManager getHOGInventoryImages not found hog %s" % hogName)
            return None

        hog = HOGImageManager.s_hogs[hogName]
        allItems = hog.getItems()

        if hogItemName not in allItems:
            Trace.log("Manager", 0, "HOGImageManager getHOGInventoryImages not found item %s" % hogItemName)
            return None

        return allItems[hogItemName]

    @staticmethod
    def addHOG(name, hog):
        HOGImageManager.s_hogs[name] = hog
