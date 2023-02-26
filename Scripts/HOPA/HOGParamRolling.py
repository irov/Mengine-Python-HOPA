from Foundation.DatabaseManager import DatabaseManager
from Foundation.DefaultManager import DefaultManager
from Foundation.DemonManager import DemonManager
from HOPA.EnigmaManager import EnigmaManager

class HOGParamRolling(object):
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
            pass

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
            pass  # def Printerer(self):  #     print self.itemName ,            self.objectName,            self.textID ,            self.difficulty ,             self.score ,            self.slot ,            self.Slot_Bind,            self.activate  # pass

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
                pass

            if _DEVELOPMENT is True:
                for item in items:
                    if item.itemName == HOGItemName:
                        Trace.log("HOGManager", 0, "HOGManager.loadHOG: HOG '%s' element '%s' dublicate" % (param, HOGItemName))

                        return False
                        pass
                    pass
                pass

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

            HOGItem = HOGParamRolling.HOGItem(HOGItemName, ObjectName, TextID, Difficulty, Score, Slot, SlotBind)
            items.append(HOGItem)
            pass

        HOGParamRolling.s_items[name] = items

        return True
        pass

    @staticmethod
    def getHOGItems(name):
        if name not in HOGParamRolling.s_items:
            Trace.log("HOGManager", 0, "HOGParamRolling.getHOGItems: no current items for HOG: %s" % name)

            return None
            pass

        return HOGParamRolling.s_items[name]
        pass

    @staticmethod
    def getSceneHOGItems(sceneName):
        enigmas = EnigmaManager.getSceneEnigmas(sceneName)
        allItems = []
        for enigmaName in enigmas:
            enigmaItems = HOGParamRolling.getHOGItems(enigmaName)
            allItems += enigmaItems
            pass

        return allItems
        pass

    @staticmethod
    def hasHOGItem(name, identity):
        items = HOGParamRolling.getHOGItems(name)

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
        items = HOGParamRolling.getHOGItems(name)

        for item in items:
            if item.itemName != identity:
                continue
                pass

            return item
            pass

        Trace.log("HOGManager", 0, "HOGParamRolling.getHOGItem: %s no found item %s" % (name, identity))

        return None
        pass

    @staticmethod
    def getInventory(name):
        if name not in HOGParamRolling.s_inventories.keys():
            inventory = DemonManager.getDemon("HOGInventory")
            return inventory
            pass

        return HOGParamRolling.s_inventories[name]
        pass

    @staticmethod
    def setInventory(name, inventory):
        HOGParamRolling.s_inventories[name] = inventory
        pass

    @staticmethod
    def hasHOGItemTextID(name, identity):
        if HOGParamRolling.hasHOGItem(name, identity) is False:
            return False
            pass

        return True
        pass

    @staticmethod
    def getHOGItemTextID(name, identity):
        item = HOGParamRolling.getHOGItem(name, identity)

        return item.textID
        pass
    pass