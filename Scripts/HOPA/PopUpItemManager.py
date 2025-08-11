from Foundation.Manager import Manager

from Foundation.DatabaseManager import DatabaseManager
from Foundation.GroupManager import GroupManager

class PopUpItemManager(Manager):
    s_items = {}

    class ItemPopUpParam(object):
        __slots__ = "inventoryItem", "group", "textID"

        def __init__(self, inventoryItem, group, textID):
            self.inventoryItem = inventoryItem
            self.group = group
            self.textID = textID
            pass

        def getInventoryItem(self):
            return self.inventoryItem

    @staticmethod
    def _onFinalize():
        PopUpItemManager.s_items = {}
        pass

    @staticmethod
    def loadParams(module, param):
        successful = True

        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            Name = record.get("Name")
            StoreGroupName = record.get("StoreGroupName")
            StoreObjectName = record.get("StoreObjectName")
            TextID = record.get("TextID")

            result = PopUpItemManager.addItem(Name, StoreGroupName, StoreObjectName, TextID)

            if result is False:
                Trace.log("Manager", 0, "PopUpItemManager inavlid loadPopUpItems item %s" % Name)
                successful = False

        return successful

    @staticmethod
    def hasItem(name):
        return name in PopUpItemManager.s_items
        pass

    @staticmethod
    def addItem(name, groupName, inventoryName, textID):
        if PopUpItemManager.hasItem(name) is True:
            Trace.log("Manager", 0, "PopUpItemManager addItem: item %s already exist" % (name))
            return False

        if GroupManager.hasGroup(groupName) is False:
            Trace.log("Manager", 0, "PopUpItemManager addItem: item %s not found group '%s'" % (name, groupName))
            return False

        group = GroupManager.getGroup(groupName)

        if group.hasObject(inventoryName) is False:
            Trace.log("Manager", 0, "PopUpItemManager addItem: item %s not found object '%s' in group '%s'" % (name, inventoryName, groupName))
            return False

        inventoryItem = group.getObject(inventoryName)

        if inventoryItem is None:
            Trace.log("Manager", 0, "ItemManager addItem: Cann't get item '%s' from group '%s'" % (name, groupName))
            return False

        item = PopUpItemManager.ItemPopUpParam(inventoryItem, group, textID)

        PopUpItemManager.s_items[name] = item

        return True

    @staticmethod
    def getItemInventoryItem(name):
        if PopUpItemManager.hasItem(name) is False:
            Trace.log("Manager", 0, "PopUpItemManager getInventoryItem: not found item %s" % (name))
            return None

        item = PopUpItemManager.s_items[name]

        return item.inventoryItem

    @staticmethod
    def getInventoryItemFindItems(inventoryItem):
        FindItems = []
        for name, item in PopUpItemManager.s_items.iteritems():
            if item.getInventoryItem() is inventoryItem:
                FindItems.append(name)

        return FindItems

    @staticmethod
    def getItemTextID(name):
        if PopUpItemManager.hasItem(name) is False:
            Trace.log("Manager", 0, "PopUpItemManager getInventoryItem: not found item %s" % (name))
            return None

        item = PopUpItemManager.s_items[name]

        return item.textID
