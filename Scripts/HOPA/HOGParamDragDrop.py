from Foundation.DatabaseManager import DatabaseManager
from Foundation.DefaultManager import DefaultManager
from Foundation.DemonManager import DemonManager
from HOPA.EnigmaManager import EnigmaManager


class HOGParamDragDrop(object):
    s_items = {}
    s_inventories = {}
    s_inventorySlots = {}

    class HOGItem(object):
        def __init__(self, itemName, objectName, textID, difficulty, score, slot, slot_bind):
            self.itemName = itemName
            self.objectName = objectName
            self.textID = textID
            self.difficulty = difficulty
            self.score = score
            self.slot = slot
            self.slot_bind = slot_bind
            self.activate = True

        def setActivate(self, value):
            self.activate = value
            pass

        def getActivate(self):
            return self.activate
            pass

        def getSlot(self):
            """
            Deprecated
            :return: str "Default" or "Clue"
            """
            return self.slot
            pass

        def setSlot(self, slot):
            self.slot = slot
            pass

        def setScore(self, score):
            self.score = score
            pass

        def getScore(self):
            return self.score
            pass

        def getTextID(self):
            return self.textID
            pass

        def getSlotBind(self):
            return self.slot_bind

    @staticmethod
    def loadHOGItems(module, param, name):
        records = DatabaseManager.getDatabaseRecords(module, param)

        items = []

        for record in records:
            HOGItemName = record.get("HOGItemName")
            ObjectName = record.get("ObjectName")
            TextID = record.get("TextID")
            Difficulty = record.get("Difficulty", 0)
            Score = record.get("Score", 0)
            Slot = record.get("Slot", "Default")
            SlotBind = record.get("Slot_Bind", None)

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

            if ObjectName is not None:
                if ItemsGroup.hasObject(ObjectName) is False:
                    Trace.log("Manager", 0, "HOGManager.loadHOGItems: group '%s'not found item %s" % (ItemsGroup.getName(), ObjectName))
                    return False

            HOGItem = HOGParamDragDrop.HOGItem(HOGItemName, ObjectName, TextID, Difficulty, Score, Slot, SlotBind)
            items.append(HOGItem)

        HOGParamDragDrop.s_items[name] = items
        return True

    @staticmethod
    def getHOGItems(name):
        if name not in HOGParamDragDrop.s_items:
            Trace.log("HOGManager", 0, "HOGParamRolling.getHOGItems: no current items for HOG: %s" % name)
            return None

        return HOGParamDragDrop.s_items[name]

    @staticmethod
    def getSceneHOGItems(sceneName):
        enigmas = EnigmaManager.getSceneEnigmas(sceneName)
        allItems = []
        for enigmaName in enigmas:
            enigmaItems = HOGParamDragDrop.getHOGItems(enigmaName)
            allItems += enigmaItems

        return allItems
        pass

    @staticmethod
    def hasHOGItem(name, identity):
        items = HOGParamDragDrop.getHOGItems(name)

        for item in items:
            if item.itemName != identity:
                continue
            return True
        return False

    @staticmethod
    def getHOGItem(name, identity):
        items = HOGParamDragDrop.getHOGItems(name)

        for item in items:
            if item.itemName != identity:
                continue
            return item

        Trace.log("HOGManager", 0, "HOGParamRolling.getHOGItem: %s no found item %s" % (name, identity))
        return None

    @staticmethod
    def getInventory(name):
        if name not in HOGParamDragDrop.s_inventories.keys():
            inventory = DemonManager.getDemon("HOGInventory")
            return inventory
            pass

        return HOGParamDragDrop.s_inventories[name]
        pass

    @staticmethod
    def setInventory(name, inventory):
        HOGParamDragDrop.s_inventories[name] = inventory
        pass

    @staticmethod
    def hasHOGItemTextID(name, identity):
        if HOGParamDragDrop.hasHOGItem(name, identity) is False:
            return False
            pass

        return True
        pass

    @staticmethod
    def getHOGItemTextID(name, identity):
        item = HOGParamDragDrop.getHOGItem(name, identity)

        return item.textID
