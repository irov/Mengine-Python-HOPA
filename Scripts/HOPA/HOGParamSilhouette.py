from Foundation.DatabaseManager import DatabaseManager
from Foundation.DefaultManager import DefaultManager
from Foundation.DemonManager import DemonManager
from Foundation.GroupManager import GroupManager
from HOPA.EnigmaManager import EnigmaManager


class HOGParamSilhouette(object):
    s_items = {}
    s_inventories = {}
    s_inventorySlots = {}

    class HOGItem(object):
        def __init__(self, itemName, objectName, storeGroupName, storeObjectName):
            self.itemName = itemName
            self.objectName = objectName

            self.storeGroupName = storeGroupName
            self.storeObjectName = storeObjectName

            self.storeObject = GroupManager.getObject(self.storeGroupName, self.storeObjectName)

            self.activate = True
            pass

        def getStoreObject(self):
            return self.storeObject

        def setActivate(self, value):
            self.activate = value
            pass

        def getActivate(self):
            return self.activate

    @staticmethod
    def loadHOGItems(module, param, name):
        records = DatabaseManager.getDatabaseRecords(module, param)

        items = []

        for record in records:
            HOGItemName = record.get("HOGItemName")
            ObjectName = record.get("ObjectName")

            StoreGroupName = record.get("StoreGroupName")
            StoreObjectName = record.get("StoreObjectName")

            if _DEVELOPMENT is True:
                for item in items:
                    if item.itemName == HOGItemName:
                        Trace.log("HOGManager", 0, "HOGManager.loadHOG: HOG '%s' element '%s' dublicate" % (param, HOGItemName))
                        return False

            HOGItemsInDemon = DefaultManager.getDefaultBool("HOGItemsInDemon", True)
            EnigmaObject = EnigmaManager.getEnigmaObject(name)

            if EnigmaObject is None:
                Trace.log("Manager", 0, 'EnigmaObject {} is None!!!'.format(name))
                return False

            if HOGItemsInDemon is True:
                ItemsGroup = EnigmaObject
                pass
            else:
                ItemsGroup = EnigmaObject.getGroup()
                pass

            if ObjectName is not None:
                if ItemsGroup.hasObject(ObjectName) is False:
                    Trace.log("Manager", 0, "HOGManager.loadHOGItems: group '%s'not found item %s" % (ItemsGroup.getName(), ObjectName))
                    return False
                    pass
                pass

            if StoreGroupName is None:
                StoreGroup = ItemsGroup
            else:
                StoreGroup = GroupManager.getGroup(StoreGroupName)

            if StoreObjectName is not None:
                if StoreGroup.hasObject(StoreObjectName) is False:
                    Trace.log("Manager", 0, "HOGManager.loadHOGItems: group '{}' is not found {}".format(StoreGroup.getName(), StoreObjectName))
                    return False
                pass
            pass

            HOGItem = HOGParamSilhouette.HOGItem(HOGItemName, ObjectName, StoreGroupName, StoreObjectName)
            items.append(HOGItem)
            pass

        HOGParamSilhouette.s_items[name] = items

        return True
        pass

    @staticmethod
    def getHOGItems(name):
        if name not in HOGParamSilhouette.s_items:
            Trace.log("HOGManager", 0, "HOGParamSilhouette.getHOGItems: no current items for HOG: %s" % name)
            return None
            pass

        return HOGParamSilhouette.s_items[name]
        pass

    @staticmethod
    def getSceneHOGItems(sceneName):
        enigmas = EnigmaManager.getSceneEnigmas(sceneName)
        allItems = []
        for enigmaName in enigmas:
            enigmaItems = HOGParamSilhouette.getHOGItems(enigmaName)
            allItems += enigmaItems
            pass

        return allItems
        pass

    @staticmethod
    def hasHOGItem(name, identity):
        items = HOGParamSilhouette.getHOGItems(name)

        for item in items:
            if item.itemName != identity:
                continue
                pass

            return True
            pass

        return False
        pass

    @staticmethod
    def getHOGItem(name, identity):
        items = HOGParamSilhouette.getHOGItems(name)

        for item in items:
            if item.itemName != identity:
                continue
                pass

            return item
            pass

        Trace.log("HOGManager", 0, "HOGParamSilhouette.getHOGItem: %s no found item %s" % (name, identity))

        return None
        pass

    @staticmethod
    def getInventory(name):
        if name not in HOGParamSilhouette.s_inventories.keys():
            inventory = DemonManager.getDemon("HOGInventory")
            return inventory
            pass

        return HOGParamSilhouette.s_inventories[name]
        pass

    @staticmethod
    def setInventory(name, inventory):
        HOGParamSilhouette.s_inventories[name] = inventory
