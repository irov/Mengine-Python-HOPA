from Foundation.DatabaseManager import DatabaseManager
from Foundation.DefaultManager import DefaultManager
from Foundation.DemonManager import DemonManager
from HOPA.EnigmaManager import EnigmaManager


class HOGParamDefault(object):
    s_items = {}

    class HOGItem(object):
        def __init__(self, itemName, objectName, textID):
            self.itemName = itemName
            self.objectName = objectName
            self.textID = textID
            pass

        def getTextID(self):
            return self.textID

    @staticmethod
    def loadHOGItems(module, param, name):
        records = DatabaseManager.getDatabaseRecords(module, param)

        items = []

        for record in records:
            HOGItemName = record.get("HOGItemName")
            ObjectName = record.get("ObjectName")
            TextID = record.get("TextID")

            if Mengine.existText(TextID) is False:
                Trace.log("HOGManager", 0, "HOGManager.loadHOG: HOG '%s' element '%s' not found text '%s'" % (param, HOGItemName, TextID))
                return False

            if _DEVELOPMENT is True:
                for item in items:
                    if item.itemName == HOGItemName:
                        Trace.log("HOGManager", 0, "HOGManager.loadHOG: HOG '%s' element '%s' dublicate" % (param, HOGItemName))
                        return False

            HOGItemsInDemon = DefaultManager.getDefaultBool("HOGItemsInDemon", True)
            EnigmaObject = EnigmaManager.getEnigmaObject(name)
            if HOGItemsInDemon is True:
                ItemsGroup = EnigmaObject
            else:
                ItemsGroup = EnigmaObject.getGroup()

            if ItemsGroup.hasObject(ObjectName) is False:
                Trace.log("Manager", 0, "HOGManager.loadHOGItems: group '%s'not found item %s" % (ItemsGroup.getName(), ObjectName))
                return False

            HOGItem = HOGParamDefault.HOGItem(HOGItemName, ObjectName, TextID)
            items.append(HOGItem)

        HOGParamDefault.s_items[name] = items

        return True

    @staticmethod
    def getInventory(name):
        inventory = DemonManager.getDemon("HOGInventory")
        return inventory

    @staticmethod
    def getHOGItems(name):
        items = HOGParamDefault.s_items[name]
        return items

    @staticmethod
    def getSceneHOGItems(sceneName):
        enigmas = EnigmaManager.getSceneEnigmas(sceneName)
        allItems = []
        for enigmaName in enigmas:
            enigmaItems = HOGParamDefault.getHOGItems(enigmaName)
            allItems += enigmaItems
        return allItems

    @staticmethod
    def hasHOGItem(name, identity):
        items = HOGParamDefault.getHOGItems(name)
        for item in items:
            if item.itemName != identity:
                continue
            return True
        return False

    @staticmethod
    def getHOGItem(name, identity):
        items = HOGParamDefault.getHOGItems(name)

        for item in items:
            if item.itemName != identity:
                continue
            return item

        Trace.log("HOGManager", 0, "HOGParamDefault.getHOGItem: %s no found item %s" % (name, identity))
        return None

    @staticmethod
    def hasHOGItemTextID(name, identity):
        if HOGParamDefault.hasHOGItem(name, identity) is False:
            return False
        return True

    @staticmethod
    def getHOGItemTextID(name, identity):
        item = HOGParamDefault.getHOGItem(name, identity)
        return item.textID
