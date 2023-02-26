from Foundation.DatabaseManager import DatabaseManager
from Foundation.DemonManager import DemonManager
from HOPA.EnigmaManager import EnigmaManager

class HOGParamFXPartsGathering(object):
    s_groups = {}
    s_items = {}
    s_inventories = {}

    class HOGItem(object):
        def __init__(self, itemName, objectName, group):
            self.name = itemName
            self.objectName = objectName
            self.group = group
            self.group.items_amount += 1
            self.activate = True

        def setActivate(self, value):
            self.activate = value

        def getActivate(self):
            return self.activate

    class HOGItemsGroup(object):
        def __init__(self, groupName, movieName):
            self.name = groupName
            self.movieName = movieName
            self.items_amount = 0

    @staticmethod
    def loadHOGItems(module, param, name):
        HOGParamFXPartsGathering.loadHOGGroups(module, param, name)

        records = DatabaseManager.getDatabaseRecords(module, param)

        items = []

        for record in records:
            ItemName = record.get('HOGItemName')
            ObjectName = record.get('ObjectName')
            GroupName = record.get('Group')

            group = HOGParamFXPartsGathering.getHOGGroup(name, GroupName)

            items.append(HOGParamFXPartsGathering.HOGItem(ItemName, ObjectName, group))

        HOGParamFXPartsGathering.s_items[name] = items

    @staticmethod
    def loadHOGGroups(module, param, name):
        records = DatabaseManager.getDatabaseRecords(module, param + '_Groups')

        groups = []

        for record in records:
            GroupName = record.get('HOGItemsGroupName')
            MovieName = record.get('MovieName')

            groups.append(HOGParamFXPartsGathering.HOGItemsGroup(GroupName, MovieName))

        HOGParamFXPartsGathering.s_groups[name] = groups

    @staticmethod
    def getHOGItems(name):
        if name not in HOGParamFXPartsGathering.s_items:
            Trace.log("HOGManager", 0, "HOGParamFXPartsGathering.getHOGItems: no current items for HOG: %s" % name)

            return None

        return HOGParamFXPartsGathering.s_items[name]

    @staticmethod
    def getHOGGroups(name):
        if name not in HOGParamFXPartsGathering.s_groups:
            Trace.log("HOGManager", 0, "HOGParamFXPartsGathering.getHOGGroups: no current groups for HOG: %s" % name)

            return None

        return HOGParamFXPartsGathering.s_groups[name]

    @staticmethod
    def getSceneHOGItems(sceneName):
        enigmas = EnigmaManager.getSceneEnigmas(sceneName)
        allItems = []
        for enigmaName in enigmas:
            enigmaItems = HOGParamFXPartsGathering.getHOGItems(enigmaName)
            allItems += enigmaItems

        return allItems

    @staticmethod
    def hasHOGItem(name, identity):
        items = HOGParamFXPartsGathering.getHOGItems(name)

        for item in items:
            if item.name != identity:
                continue

            return True

        return False

    @staticmethod
    def getHOGItem(name, identity):
        items = HOGParamFXPartsGathering.getHOGItems(name)

        for item in items:
            if item.name != identity:
                continue

            return item

        Trace.log("HOGManager", 0, "HOGParamFXPartsGathering.getHOGItem: %s no found item %s" % (name, identity))

        return None

    @staticmethod
    def getHOGGroup(name, identity):
        groups = HOGParamFXPartsGathering.getHOGGroups(name)

        for group in groups:
            if group.name != identity:
                continue

            return group

        Trace.log("HOGManager", 0, "HOGParamFXPartsGathering.getHOGGroup: %s no found group %s" % (name, identity))

        return None

    @staticmethod
    def getInventory(name):
        if name not in HOGParamFXPartsGathering.s_inventories.keys():
            inventory = DemonManager.getDemon("HOGInventoryFXPartsGathering")
            return inventory

        return HOGParamFXPartsGathering.s_inventories[name]

    @staticmethod
    def setInventory(name, inventory):
        HOGParamFXPartsGathering.s_inventories[name] = inventory