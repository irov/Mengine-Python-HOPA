from Foundation.Manager import Manager

from Foundation.DatabaseManager import DatabaseManager
from Foundation.GroupManager import GroupManager

class BonusItemManager(Manager):
    s_items = {}
    s_bonusItems = []

    class BonusItem(object):
        def __init__(self, params):
            self.params = params

    @staticmethod
    def _onFinalize():
        BonusItemManager.s_items = {}
        BonusItemManager.s_bonusItems = []
        pass

    @staticmethod
    def loadBonusItems(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)
        sceneDict = {}
        for value in records:
            SceneName = value.get("SceneName")
            GroupName = value.get("GroupName")
            ItemNames = value.get("Items")
            if SceneName in sceneDict:
                internalDict = sceneDict[SceneName]
                internalDict[GroupName] = ItemNames
                pass
            else:
                internalDict = {}
                internalDict[GroupName] = ItemNames
                sceneDict[SceneName] = internalDict
                pass
            for itemName in ItemNames:
                Item = GroupManager.getObject(GroupName, itemName)
                BonusItemManager.s_bonusItems.append(Item)
                pass
            BonusItemManager.s_items = sceneDict
        pass

    @staticmethod
    def hasBonusItem(sceneName):
        if sceneName in BonusItemManager.s_items:
            bonus = BonusItemManager.s_items[sceneName]
            return bonus
        return []
        pass

    @staticmethod
    def getBonusItem():
        return BonusItemManager.s_bonusItems
        pass

    # ----------------------------------not usable part below-------------------#
    @staticmethod
    def addItem(name, sceneGroupName, sceneObjectName, storeGroupName, storeObjectName, partName):
        if name in BonusItemManager.s_items:
            Trace.log("Manager", 0, "BonusItemManager addItem: item %s already exist" % (name))
            return
            pass

        SceneObject = None

        if sceneGroupName is not None and sceneObjectName is not None:
            SceneObject = GroupManager.getObject(sceneGroupName, sceneObjectName)
            objType = SceneObject.getParam("Type")
            if objType != "Socket":
                Trace.log("Manager", 0, "BonusItemManager.addItem name: %s sceneObject invalid Type %s must be Socket" % (name, objType))
                pass
            pass

        StoreObject = GroupManager.getObject(storeGroupName, storeObjectName)

        PartObject = StoreObject.getObject(partName)
        PartObject.setEnable(False)

        StoreObject.appendParam("FindItems", SceneObject)

        item = BonusItemManager.Item(SceneObject, StoreObject, PartObject)

        BonusItemManager.s_items[name] = item
        pass

    @staticmethod
    def disableBonusItems():
        for item in BonusItemManager.s_items.itervalues():
            item.partObject.setEnable(False)
            pass
        pass

    @staticmethod
    def getItem(name):
        if BonusItemManager.hasItem(name) is False:
            Trace.log("BonusItemManager", 0, "BonusItemManager.getItem: not found item %s" % (name))

            return None
            pass

        item = BonusItemManager.s_items[name]

        return item
        pass

    @staticmethod
    def hasItemSceneObject(name):
        if BonusItemManager.hasItem(name) is False:
            return False
            pass

        item = BonusItemManager.getItem(name)

        if item.sceneObject is None:
            return False
            pass

        return True
        pass

    @staticmethod
    def getItemSceneObject(name):
        item = BonusItemManager.getItem(name)

        return item.sceneObject
        pass

    @staticmethod
    def hasItemStoreObject(name):
        if BonusItemManager.hasItem(name) is False:
            return False
            pass

        item = BonusItemManager.getItem(name)

        if item.storeObject is None:
            return False
            pass

        return True
        pass

    @staticmethod
    def getItemStoreObject(name):
        item = BonusItemManager.getItem(name)

        return item.storeObject
        pass

    @staticmethod
    def findItemStoreObject(storeObjectName):
        for name, item in BonusItemManager.s_items.iteritems():
            if item.storeObject.name == storeObjectName:
                return item.storeObject
                pass
            pass

        Trace.log("ItemManager", 0, "BonusItemManager.findItemStoreObject: not found item %s" % (storeObjectName))

        return None
        pass

    @staticmethod
    def getItemPartObject(name):
        item = BonusItemManager.getItem(name)

        return item.partObject
        pass

    @staticmethod
    def getItemPartStartPosition(name):
        item = BonusItemManager.getItem(name)
        objType = item.sceneObject.getType()
        entitySceneObject = item.sceneObject.getEntity()
        if objType == "ObjectSocket":
            hotspot = entitySceneObject.hotspot
            position = hotspot.getWorldPolygonCenter()
            pass
        else:
            position = entitySceneObject.getLocalPosition()
            pass

        return position
