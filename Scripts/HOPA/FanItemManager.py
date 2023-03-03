from Foundation.DatabaseManager import DatabaseManager
from Foundation.GroupManager import GroupManager


class FanItemManager(object):
    s_items = {}

    class FanItem(object):
        def __init__(self, FanItem, ObjectItem):
            self.FanItem = FanItem
            self.ObjectItem = ObjectItem

    @staticmethod
    def loadFanItem(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            name = record.get("ItemName")
            ObjectGroupName = record.get("ObjectGroupName")
            ObjectItemName = record.get("ObjectName")

            FanItemGroupName = record.get("FanItemGroupName")
            FanItemName = record.get("FanItemName")

            FanItemManager.addItem(name, FanItemGroupName, FanItemName, ObjectGroupName, ObjectItemName)

    @staticmethod
    def addItem(name, FanItemGroupName, FanItemName, ObjectGroupName, ObjectItemName):
        if FanItemManager.hasItem(name) is True:
            return

        FanItem = GroupManager.getObject(FanItemGroupName, FanItemName)
        ObjectItem = GroupManager.getObject(ObjectGroupName, ObjectItemName)

        item = FanItemManager.FanItem(FanItem, ObjectItem)

        FanItemManager.s_items[name] = item

    ##Item
    @staticmethod
    def hasItem(name):
        if name not in FanItemManager.s_items:
            return False

        return True
        pass

    @staticmethod
    def getItem(name):
        if FanItemManager.hasItem(name) is False:
            Trace.log("FanItemManager", 0, "FanItemManager.getFan: not found item %s" % (name))
            return None

        item = FanItemManager.s_items[name]

        return item
        pass

    @staticmethod
    def hasItemFanItem(name):
        item = FanItemManager.getItem(name)

        if item is None:
            return False
            pass

        if item.FanItem is None:
            return False
            pass

        return True
        pass

    @staticmethod
    def getItemFanItem(name):
        item = FanItemManager.getItem(name)

        return item.FanItem
        pass

    @staticmethod
    def hasItemObject(name):
        item = FanItemManager.getItem(name)

        if item is None:
            return False
            pass

        if item.ObjectItem is None:
            return False
            pass

        return True
        pass

    @staticmethod
    def getItemObject(name):
        item = FanItemManager.getItem(name)
        if name is None:
            Trace.log("Manager", 0, "Error: no getItemObject(name)")
            return
            pass

        return item.ObjectItem
