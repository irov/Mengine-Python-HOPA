from Foundation.Manager import Manager

from Foundation.DatabaseManager import DatabaseManager
from Foundation.GroupManager import GroupManager


class HOGFittingItemManager(Manager):
    s_items = {}

    class HOGItem(object):
        def __init__(self, HOGItemName, SceneObjectName, SceneGroupName, StoreObjectName, StoreHideObjectName,
                     StoreGroupName, textID, StoreZoomObjectName):
            self.HOGItemName = HOGItemName
            self.SceneObjectName = SceneObjectName
            self.SceneGroupName = SceneGroupName

            self.StoreObjectName = StoreObjectName
            self.StoreHideObjectName = StoreHideObjectName
            self.StoreGroupName = StoreGroupName

            self.SceneObject = None
            if self.SceneGroupName is not None and self.SceneObjectName is not None:
                self.SceneObject = GroupManager.getObject(SceneGroupName, SceneObjectName)

            self.StoreObject = GroupManager.getObject(StoreGroupName, StoreObjectName)
            self.StoreHideObject = GroupManager.getObject(StoreGroupName, StoreHideObjectName)
            self.textID = textID

            self.StoreZoomObjectName = StoreZoomObjectName

            if GroupManager.hasObject(StoreGroupName, StoreZoomObjectName):
                self.StoreZoomObject = GroupManager.getObject(StoreGroupName, StoreZoomObjectName)
            else:
                self.StoreZoomObject = None

    @staticmethod
    def _onFinalize():
        HOGFittingItemManager.s_items = {}
        pass

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)
        for record in records:
            HOGItemName = record.get("HOGItemName")
            if HOGItemName is None or HOGItemName[0] == "#":
                continue

            if (HOGItemName in HOGFittingItemManager.s_items):
                Trace.log("Manager", 0, "HOGFittingItemManager.loadInventoryItems: item with name '%s' already loadet two items with one name" % (HOGItemName))
                continue

            SceneObjectName = record.get("SceneObjectName")
            SceneGroupName = record.get("SceneGroupName")

            StoreObjectName = record.get("StoreObjectName")
            StoreHideObjectName = record.get("StoreHideObjectName")
            StoreGroupName = record.get("StoreGroupName")
            textID = record.get("TextID", None)
            StoreZoomObjectName = record.get("StoreZoomObjectName", None)

            # if HOGFittingItemManager.CheckFindGroup(SceneGroupName) is False:
            #     return False

            # SceneGroup = GroupManager.getGroup(SceneGroupName)
            #
            # if SceneGroup.hasObject(SceneObjectName) is False:
            #     HOGFittingItemManager.PrintNotFindItem(SceneObjectName, SceneGroupName)
            #     return False
            #     pass

            if HOGFittingItemManager.CheckFindGroup(StoreGroupName) is False:
                return False

            StoreGroup = GroupManager.getGroup(StoreGroupName)

            if StoreGroup.hasObject(StoreObjectName) is False:
                HOGFittingItemManager.PrintNotFindItem(StoreObjectName, StoreGroupName)
                return False

            if StoreGroup.hasObject(StoreHideObjectName) is False:
                HOGFittingItemManager.PrintNotFindItem(StoreHideObjectName, StoreGroupName)
                return False

            HOGItem = HOGFittingItemManager.HOGItem(HOGItemName, SceneObjectName, SceneGroupName, StoreObjectName,
                                                    StoreHideObjectName, StoreGroupName, textID, StoreZoomObjectName)
            HOGFittingItemManager.s_items[HOGItemName] = HOGItem

        return True

    @staticmethod
    def CheckFindGroup(GroupName):
        if GroupManager.hasGroup(GroupName) is False:
            Trace.log("Manager", 0, "HOGFittingItemManager.CheckFindGroup: group '%s'not found" % (GroupName))
            return False
        return True

    @staticmethod
    def PrintNotFindItem(ItemName, GroupName):
        Trace.log("Manager", 0, "HOGFittingItemManager.PrintNotFindItem: group '%s'not found item %s" % (GroupName, ItemName))

    @staticmethod
    def hasItem(name):
        return name in HOGFittingItemManager.s_items

    @staticmethod
    def getItem(name):
        if HOGFittingItemManager.hasItem(name) is False:
            Trace.log("Manager", 0, "HOGFittingItemManager.getItem: not found item %s" % (name))
            return None
        item = HOGFittingItemManager.s_items[name]
        return item

    @staticmethod
    def getTextID(name):
        item = HOGFittingItemManager.getItem(name)
        if item is None:
            return None
        return item.textID

    @staticmethod
    def getInventoryItemKey(invItem):
        for key, item in HOGFittingItemManager.s_items.iteritems():
            if item.StoreObject == invItem or item.StoreHideObject == invItem:
                return key
        return None

    @staticmethod
    def getItemSceneObject(name):
        item = HOGFittingItemManager.getItem(name)
        return item.SceneObject

    @staticmethod
    def getItemStoreObject(name):
        item = HOGFittingItemManager.getItem(name)
        return item.StoreObject

    @staticmethod
    def getItemStoreZoomObject(name):
        item = HOGFittingItemManager.getItem(name)
        return item.StoreZoomObject

    @staticmethod
    def getItemObject(name, inv):
        invEntity = inv.getEntity()
        slot = invEntity.getSlotByName(name)

        item = HOGFittingItemManager.getItem(name)
        if slot.SlotIsFitting is False:
            return item.StoreObject
        else:
            return item.StoreHideObject
