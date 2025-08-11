from Foundation.Manager import Manager

from Foundation.DatabaseManager import DatabaseManager
from Foundation.GroupManager import GroupManager

class ZenElementsManager(Manager):
    s_objects = {}

    class SingleZen(object):
        def __init__(self, ExternalMovie, InternalMovie, ItemList, PlacementList, SocketIn, SocketEx, InSlots, ExSlots):
            self.ExternalMovie = ExternalMovie  # OBJ
            self.InternalMovie = InternalMovie
            self.ItemList = ItemList
            self.PlacementList = PlacementList
            self.SocketIn = SocketIn  # OBJ
            self.SocketEx = SocketEx
            self.InSlots = InSlots
            self.ExSlots = ExSlots

        def getItems(self):
            return self.ItemList
            pass

        def getExternalMovieDetail(self):
            return {"Movie": self.ExternalMovie, "Socket": self.SocketEx, "Slots": self.ExSlots}
            pass

        def getInternalMovieDetail(self):
            return {"Movie": self.InternalMovie, "Socket": self.SocketIn, "Slots": self.InSlots}
            pass

        def getWinPlacement(self):
            return self.PlacementList

    @staticmethod
    def _onFinalize():
        ZenElementsManager.s_objects = {}
        pass

    @staticmethod
    def loadZens(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for values in records:
            objectName = values.get("Name")
            if objectName == "":
                continue
            groupName = values.get("GroupName")
            ZenElementsManager.loadZenCollection(objectName, groupName, module, param)

    @staticmethod
    def loadZenCollection(objectName, groupName, module, param):
        EnigmaObject = GroupManager.getObject(groupName, "Demon_%s" % (objectName))
        records = DatabaseManager.getDatabaseRecords(module, param)

        for values in records:
            ExternalMovie = values.get("ExternalMovie")
            ExternalMovie = EnigmaObject.getObject(ExternalMovie)

            InternalMovie = values.get("InternalMovie")
            InternalMovie = EnigmaObject.getObject(InternalMovie)

            PlacementMode = values.get("PlaceList")
            ItemList = values.get("ItemList")
            SocketIn = values.get("SocketIn")
            SocketEx = values.get("SocketEx")
            InSlots = values.get("InSlots")
            ExSlots = values.get("ExSlots")
            placement = []

            mini_records = DatabaseManager.getDatabaseRecords(module, PlacementMode)
            for val in mini_records:
                item_name = val.get("Name")
                placement.append(item_name)

            Object = ZenElementsManager.SingleZen(ExternalMovie, InternalMovie, ItemList, placement,
                                                  SocketIn, SocketEx,InSlots, ExSlots)
            ZenElementsManager.s_objects[objectName] = Object
        pass

    @staticmethod
    def getZen(name):
        if name not in ZenElementsManager.s_objects.keys():
            return None
            pass

        return ZenElementsManager.s_objects[name]
        pass

    @staticmethod
    def hasZen(name):
        if name not in ZenElementsManager.s_objects.keys():
            return False
            pass
        return True
        pass

    @staticmethod
    def getItems(name):
        zen = ZenElementsManager.getZen(name)
        return zen.getItems()

    @staticmethod
    def getInternalMovieDetail(name):
        zen = ZenElementsManager.getZen(name)
        return zen.getInternalMovieDetail()

    @staticmethod
    def getExternalMovieDetail(name):
        zen = ZenElementsManager.getZen(name)
        return zen.getExternalMovieDetail()

    @staticmethod
    def getWinPlacement(name):
        zen = ZenElementsManager.getZen(name)
        return zen.getWinPlacement()
