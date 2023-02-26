from Foundation.DatabaseManager import DatabaseManager
from Foundation.GroupManager import GroupManager
from Foundation.Manager import Manager

class ItemManager(Manager):
    s_items = {}

    s_currentItemPlusName = None

    @staticmethod
    def getAllItems():
        return ItemManager.s_items
        pass

    class Item(object):
        def __init__(self, itemID, itemGroupName, itemName, invItemGroupName, invItemName, textID, PlusScene, PartSubMovieName, ItemPartsCount):
            self.itemID = itemID
            self.itemGroupName = itemGroupName
            self.itemName = itemName
            self.invItemGroupName = invItemGroupName
            self.invItemName = invItemName

            self.textID = textID
            self.PlusScene = PlusScene

            self.PartSubMovieName = PartSubMovieName
            self.ItemPartsCount = ItemPartsCount

        def getItem(self):
            if self.itemName is None:
                return None
                pass

            item = GroupManager.getObject(self.itemGroupName, self.itemName)
            return item
            pass

        def getInventoryItem(self):
            if self.invItemName is None:
                return None
                pass

            invItem = GroupManager.getObject(self.invItemGroupName, self.invItemName)
            return invItem
            pass
        pass

    @staticmethod
    def _onInitialize():
        ItemManager.addObserver(Notificator.onItemZoomEnter, ItemManager.__onItemZoomEnter)
        ItemManager.addObserver(Notificator.onItemZoomLeaveOpenZoom, ItemManager.__onItemZoomLeaveOpenZoom)
        pass

    @staticmethod
    def __onItemZoomEnter(GroupZoom, ScenePlus):
        ItemManager.s_currentItemPlusName = ScenePlus

        return False
        pass

    @staticmethod
    def __onItemZoomLeaveOpenZoom(*args):
        ItemManager.s_currentItemPlusName = None

        return False
        pass

    @staticmethod
    def getCurrentItemPlusName():
        return ItemManager.s_currentItemPlusName
        pass

    @staticmethod
    def isItemPlusNameEnter(ItemPlusName):
        return ItemManager.s_currentItemPlusName == ItemPlusName
        pass

    @staticmethod
    def _onFinalize():
        ItemManager.s_items = {}
        pass

    @staticmethod
    def loadParams(module, param):
        successful = True

        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            Name = record.get("Name")
            if Name is None:
                continue
                pass

            GroupName = record.get("GroupName")
            ObjectName = record.get("ObjectName")
            StroreGroupName = record.get("StroreGroupName")
            StoreObjectName = record.get("StoreObjectName")
            TextID = record.get("TextID")
            PlusScene = record.get("PlusScene", None)
            PartSubMovieName = record.get("PartSubMovieName", None)
            ItemPartsCount = record.get("ItemPartsCount", None)

            result = ItemManager.addItem(Name, GroupName, ObjectName, StroreGroupName, StoreObjectName, TextID, PlusScene, PartSubMovieName, ItemPartsCount)

            if result is False:
                Trace.log("Manager", 0, "ItemManager inavlid loadInventoryItems item %s" % Name)

                successful = False
                pass
            pass

        return successful
        pass

    @staticmethod
    def addItem(name, groupName, objectName, inventoryItemGroupName, inventoryItemName, TextID, PlusScene, PartSubMovieName, ItemPartsCount):
        if name in ItemManager.s_items:
            Trace.log("Manager", 0, "ItemManager addItem: item %s already exist" % (name))

            return False
            pass

        if inventoryItemName is None:
            Trace.log("Manager", 0, "ItemManager addItem: StoreObjectName is None", name)

            return False
            pass

        if groupName is not None:
            if objectName is None:
                Trace.log("Manager", 0, "ItemManager addItem: item '%s' objectName = None, GroupName = '%s', you forgot add in InventoryItems.xls objectName" % (name, groupName))

                return False
                pass
            pass
        else:
            if objectName is not None:
                Trace.log("Manager", 0, "ItemManager addItem: item '%s' GroupName = None, you forgot add in InventoryItems.xls" % (objectName))

                return False
                pass
            pass

        if PlusScene is not None:
            if GroupManager.hasGroup(PlusScene) is None:
                Trace.log("Manager", 0, "ItemManager addItem: item can't find PlusScene Group '%s'" % (PlusScene))

                return False
                pass
            pass

        if Mengine.existText(TextID) is False:
            Trace.log("Manager", 0, "ItemManager addItem: Warning!! Item with key [%s] has no text for textID [%s]" % (name, TextID))

            return False
            pass

        item = ItemManager.Item(name, groupName, objectName, inventoryItemGroupName, inventoryItemName, TextID, PlusScene, PartSubMovieName, ItemPartsCount)

        ItemManager.s_items[name] = item

        return True
        pass

    @staticmethod
    def hasItem(name):
        return name in ItemManager.s_items
        pass

    @staticmethod
    def getItem(name):
        if ItemManager.hasItem(name) is False:
            Trace.log("ItemManager", 0, "ItemManager.getItem: not found item %s" % (name))

            return None
            pass

        item = ItemManager.s_items[name]

        return item
        pass

    @staticmethod
    def hasItemObject(name):
        if ItemManager.hasItem(name) is False:
            return False
            pass

        item = ItemManager.getItem(name)

        return item.getItem() is not None
        pass

    @staticmethod
    def getInventoryItemFindItems(inventoryItem):
        FindItems = []
        for name, item in ItemManager.s_items.iteritems():
            if item.getInventoryItem() is inventoryItem:
                FindItems.append(name)
                pass
            pass

        return FindItems
        pass

    @staticmethod
    def getItemObject(name, check=False):
        item = ItemManager.getItem(name)

        if item.getItem() is None:
            if check is True:
                Trace.log("ItemManager", 0, "ItemManager.getItemObject not found objectItem with %s name" % (name))
            return None
            pass

        return item.getItem()
        pass

    @staticmethod
    def hasItemInventoryItem(name):
        if ItemManager.hasItem(name) is False:
            return False
            pass

        item = ItemManager.getItem(name)

        return item.getInventoryItem() is not None
        pass

    @staticmethod
    def getItemInventoryItem(name):
        item = ItemManager.getItem(name)

        if item is None:
            return None
            pass

        return item.getInventoryItem()
        pass

    @staticmethod
    def getInventoryItemKey(invItem):
        for key, item in ItemManager.s_items.iteritems():
            if item.getInventoryItem() == invItem:
                return key
                pass

        return None
        pass

    @staticmethod
    def hasTextID(name):
        if ItemManager.hasItem(name) is False:
            return False
            pass

        item = ItemManager.getItem(name)

        return item.textID is not None
        pass

    @staticmethod
    def getTextID(name):
        item = ItemManager.getItem(name)

        if item is None:
            return None
            pass

        return item.textID
        pass
    pass

    @staticmethod
    def findItemByScenePlus(plusScene):
        for item in ItemManager.s_items.itervalues():
            if item.PlusScene == plusScene:
                return item