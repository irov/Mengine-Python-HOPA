from Foundation.DatabaseManager import DatabaseManager
from Foundation.GroupManager import GroupManager
from Foundation.Manager import Manager


class ItemManager(Manager):
    s_items = {}
    s_currentItemPlusName = None

    @staticmethod
    def getAllItems():
        return ItemManager.s_items

    class Item(object):
        def __init__(self, itemID, itemGroupName, itemName, invItemGroupName, invItemName, textID, PlusScene,
                     PartSubMovieName, ItemPartsCount, promoID):
            self.itemID = itemID
            self.itemGroupName = itemGroupName
            self.itemName = itemName
            self.invItemGroupName = invItemGroupName
            self.invItemName = invItemName

            self.textID = textID
            self.PlusScene = PlusScene

            self.PartSubMovieName = PartSubMovieName
            self.ItemPartsCount = ItemPartsCount

            self.promoID = promoID

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
            ItemPromoID = record.get("PromoId", None)

            result = ItemManager.addItem(Name, GroupName, ObjectName, StroreGroupName, StoreObjectName, TextID,
                                         PlusScene, PartSubMovieName, ItemPartsCount, ItemPromoID)

            if result is False:
                Trace.log("Manager", 0, "ItemManager invalid loadInventoryItems item %s" % Name)

                successful = False

        return successful
        pass

    @staticmethod
    def addItem(name, groupName, objectName, inventoryItemGroupName, inventoryItemName, TextID, PlusScene,
                PartSubMovieName, ItemPartsCount, ItemPromoID):
        if name in ItemManager.s_items:
            Trace.log("Manager", 0, "ItemManager addItem: item %s already exist" % (name))
            return False

        if inventoryItemName is None:
            Trace.log("Manager", 0, "ItemManager addItem: StoreObjectName is None", name)
            return False

        if groupName is not None:
            if objectName is None:
                Trace.log("Manager", 0, "ItemManager addItem: item '%s' objectName = None, GroupName = '%s', you forgot add in InventoryItems.xls objectName" % (name, groupName))
                return False
        else:
            if objectName is not None:
                Trace.log("Manager", 0, "ItemManager addItem: item '%s' GroupName = None, you forgot add in InventoryItems.xls" % (objectName))
                return False

        if PlusScene is not None:
            if GroupManager.hasGroup(PlusScene) is None:
                Trace.log("Manager", 0, "ItemManager addItem: item can't find PlusScene Group '%s'" % (PlusScene))
                return False

        if Mengine.existText(TextID) is False:
            Trace.log("Manager", 0, "ItemManager addItem: Warning!! Item with key [%s] has no text for textID [%s]" % (name, TextID))
            return False

        item = ItemManager.Item(name, groupName, objectName, inventoryItemGroupName, inventoryItemName, TextID,
                                PlusScene, PartSubMovieName, ItemPartsCount, ItemPromoID)

        ItemManager.s_items[name] = item

        return True

    @staticmethod
    def hasItem(name):
        return name in ItemManager.s_items
        pass

    @staticmethod
    def getItem(name):
        if ItemManager.hasItem(name) is False:
            Trace.log("ItemManager", 0, "ItemManager.getItem: not found item %s" % (name))
            return None

        item = ItemManager.s_items[name]
        return item

    @staticmethod
    def hasItemObject(name):
        if ItemManager.hasItem(name) is False:
            return False

        item = ItemManager.getItem(name)
        return item.getItem() is not None

    @staticmethod
    def getInventoryItemFindItems(inventoryItem):
        FindItems = []
        for name, item in ItemManager.s_items.iteritems():
            if item.getInventoryItem() is inventoryItem:
                FindItems.append(name)
        return FindItems
        pass

    @staticmethod
    def getItemObject(name, check=False):
        item = ItemManager.getItem(name)

        if item.getItem() is None:
            if check is True:
                Trace.log("ItemManager", 0, "ItemManager.getItemObject not found objectItem with %s name" % (name))
            return None

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

    @staticmethod
    def getTextID(name):
        item = ItemManager.getItem(name)

        if item is None:
            return None
            pass

        return item.textID

    @staticmethod
    def findItemByScenePlus(plusScene):
        for item in ItemManager.s_items.itervalues():
            if item.PlusScene == plusScene:
                return item
