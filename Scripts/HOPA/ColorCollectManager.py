from Foundation.Manager import Manager
from Foundation.DatabaseManager import DatabaseManager
from TraceManager import TraceManager


class ColorCollectManager(Manager):
    s_objects = {}

    class ColorCollect(object):
        def __init__(self, bulbs, items, rules, size):
            self.bulbs = bulbs
            self.items = items
            self.rules = rules
            self.size = size
            pass

        def getSize(self):
            return self.size

        def getBulbs(self):
            return self.bulbs

        def getItems(self):
            return self.items

        def getRules(self):
            return self.rules

        def getItemByName(self, name):
            return self.items[name]

        def getBulbByName(self, name):
            return self.bulbs[name]

    class Bulb(object):
        def __init__(self, bulbMovieName, socketBeginName, socketEndName, itemNames):
            self.movieName = bulbMovieName
            self.socketBeginName = socketBeginName
            self.socketEndName = socketEndName
            self.itemNames = itemNames
            pass

        def getMovieName(self):
            return self.movieName

        def getSocketBeginName(self):
            return self.socketBeginName

        def getSocketEndName(self):
            return self.socketEndName

        def getItemNames(self):
            return self.itemNames

    @staticmethod
    def _onFinalize():
        ColorCollectManager.s_objects = {}
        pass

    @staticmethod
    def loadParams(module, name):
        TraceManager.addTrace("ColorCollectManager")
        records = DatabaseManager.getDatabaseRecords(module, name)

        for values in records:
            enigmaName = values.get("EnigmaName")
            collectionBulbsParam = values.get("Bulbs")
            collectionItemsParam = values.get("Items")
            collectionRulesParam = values.get("Rules")
            size = values.get("Size")
            bulbs = ColorCollectManager.loadColorCollectBulbs(module, collectionBulbsParam)
            items = ColorCollectManager.loadColorCollectItems(module, collectionItemsParam)
            rules = ColorCollectManager.loadColorCollectRules(module, collectionRulesParam)

            game = ColorCollectManager.ColorCollect(bulbs, items, rules, size)
            ColorCollectManager.s_objects[enigmaName] = game
            pass

        return True
        pass

    @staticmethod
    def loadColorCollectBulbs(module, collectionParam):
        records = DatabaseManager.getDatabaseRecords(module, collectionParam)

        bulbs = {}
        for values in records:
            bulbMovieName = values.get("BulbMovieName")
            socketBeginName = values.get("SocketBeginObjectName")
            socketEndName = values.get("SocketEndObjectName")
            itemNames = values.get("ItemName")

            bulb = ColorCollectManager.Bulb(bulbMovieName, socketBeginName, socketEndName, itemNames)

            bulbs[bulbMovieName] = bulb
            pass

        return bulbs
        pass

    @staticmethod
    def loadColorCollectItems(module, collectionParam):
        records = DatabaseManager.getDatabaseRecords(module, collectionParam)

        items = {}

        for values in records:
            itemName = values.get("ItemName")
            slotName = values.get("SlotName")
            items[itemName] = slotName
            pass
        return items
        pass

    @staticmethod
    def loadColorCollectRules(module, collectionParam):
        records = DatabaseManager.getDatabaseRecords(module, collectionParam)

        rules = {}

        for values in records:
            movieName = values.get("MovieName")
            itemName = values.get("ItemName")
            rules[itemName] = movieName
            pass

        return rules
        pass

    @staticmethod
    def getColorCollect(name):
        if ColorCollectManager.hasColorCollect(name) is False:
            return None
            pass
        record = ColorCollectManager.s_objects[name]
        return record
        pass

    @staticmethod
    def hasColorCollect(name):
        if name not in ColorCollectManager.s_objects:
            Trace.log("ColorCollectManager", 0, "ColorCollectManager.hasColorCollect: : invalid enigmaName")
            return False
            pass
        return True
