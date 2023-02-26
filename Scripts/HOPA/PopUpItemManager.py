from Foundation.DatabaseManager import DatabaseManager
from Foundation.GroupManager import GroupManager

class PopUpItemManager(object):
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
            pass
        pass

    @staticmethod
    def onFinalize():
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
                pass
            pass

        return successful
        pass

    @staticmethod
    def hasItem(name):
        return name in PopUpItemManager.s_items
        pass

    @staticmethod
    def addItem(name, groupName, inventoryName, textID):
        if PopUpItemManager.hasItem(name) is True:
            Trace.log("Manager", 0, "PopUpItemManager addItem: item %s already exist" % (name))

            return False
            pass

        if GroupManager.hasGroup(groupName) is False:
            Trace.log("Manager", 0, "PopUpItemManager addItem: item %s not found group '%s'" % (name, groupName))

            return False
            pass

        group = GroupManager.getGroup(groupName)

        if group.hasObject(inventoryName) is False:
            Trace.log("Manager", 0, "PopUpItemManager addItem: item %s not found object '%s' in group '%s'" % (name, inventoryName, groupName))

            return False
            pass

        inventoryItem = group.getObject(inventoryName)

        if inventoryItem is None:
            Trace.log("Manager", 0, "ItemManager addItem: Cann't get item '%s' from group '%s'" % (name, groupName))

            return False
            pass

        item = PopUpItemManager.ItemPopUpParam(inventoryItem, group, textID)

        PopUpItemManager.s_items[name] = item

        return True
        pass

    @staticmethod
    def getItemInventoryItem(name):
        if PopUpItemManager.hasItem(name) is False:
            Trace.log("Manager", 0, "PopUpItemManager getInventoryItem: not found item %s" % (name))

            return None
            pass

        item = PopUpItemManager.s_items[name]

        return item.inventoryItem
        pass

    @staticmethod
    def getInventoryItemFindItems(inventoryItem):
        FindItems = []
        for name, item in PopUpItemManager.s_items.iteritems():
            if item.getInventoryItem() is inventoryItem:
                FindItems.append(name)
                pass
            pass

        return FindItems
        pass

    @staticmethod
    def getItemTextID(name):
        if PopUpItemManager.hasItem(name) is False:
            Trace.log("Manager", 0, "PopUpItemManager getInventoryItem: not found item %s" % (name))

            return None
            pass

        item = PopUpItemManager.s_items[name]

        return item.textID
        pass
    pass