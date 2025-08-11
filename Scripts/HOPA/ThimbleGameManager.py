from Foundation.Manager import Manager

from Foundation.DatabaseManager import DatabaseManager
from Foundation.GroupManager import GroupManager
from TraceManager import TraceManager

class ThimbleGameManager(Manager):
    s_objects = {}

    class ThimbleGame(object):
        def __init__(self):  # all args are list except first
            self.moves = {}
            self.shows = {}
            self.thimbles = {}
            self.sockets = {}

    @staticmethod
    def _onFinalize():
        ThimbleGameManager.s_objects = {}
        pass

    @staticmethod
    def loadParams(module, param):
        TraceManager.addTrace("ThimbleGameManager")
        records = DatabaseManager.getDatabaseRecords(module, param)

        for values in records:
            objectName = values.get("Name")
            if objectName == "":
                continue

            sceneName = values.get("SceneName")
            groupName = values.get("GroupName")
            moves = values.get("Moves")
            shows = values.get("Shows")
            thimbles = values.get("Thimbles")
            sockets = values.get("Sockets")
            ThimbleGameManager.loadThimbleGameCollection(objectName, sceneName, groupName, module, moves, shows,
                                                         thimbles, sockets)

    @staticmethod
    def loadThimbleGameCollection(objectName, sceneName, groupName, module, moves, shows, thimbles, sockets):
        EnigmaObject = GroupManager.getObject(groupName, "Demon_%s" % (objectName))
        # EnigmaObject.onEnigmaInit(objectName)
        Object = ThimbleGameManager.ThimbleGame()

        ThimbleGameManager.loadMoves(Object, module, moves)
        ThimbleGameManager.loadShows(Object, module, shows)
        ThimbleGameManager.loadThimbles(Object, module, thimbles)
        ThimbleGameManager.loadSockets(Object, module, sockets)

        ThimbleGameManager.s_objects[objectName] = Object

        pass

    @staticmethod
    def loadMoves(Object, module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)
        for value in records:
            SlotFrom = value.get("SlotFrom")
            SlotTo = value.get("SlotTo")
            Movie = value.get("ObjectName")
            Object.moves[(SlotFrom, SlotTo)] = Movie
            pass
        pass

    @staticmethod
    def loadShows(Object, module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)
        for value in records:
            SlotId = value.get("SlotId")
            Movie = value.get("ObjectName")
            Object.shows[SlotId] = Movie
            pass
        pass

    @staticmethod
    def loadThimbles(Object, module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)
        for value in records:
            SlotId = value.get("SlotId")
            ObjectName = value.get("ObjectName")
            Object.thimbles[ObjectName] = SlotId
            pass
        pass

    @staticmethod
    def loadSockets(Object, module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)
        for value in records:
            SlotId = value.get("SlotId")
            ObjectName = value.get("ObjectName")
            Object.sockets[SlotId] = ObjectName
            pass
        pass

    @staticmethod
    def getGame(name):
        if not ThimbleGameManager.hasGame(name):
            return None
            pass
        record = ThimbleGameManager.s_objects[name]
        return record
        pass

    @staticmethod
    def getEnigmaObject(name):
        if not ThimbleGameManager.hasGame(name):
            return None
            pass
        record = ThimbleGameManager.s_objects[name]
        return record.getEnigmaObject()
        pass

    @staticmethod
    def hasGame(name):
        if name not in ThimbleGameManager.s_objects:
            Trace.log("ThimbleGameManager", 0, "ThimbleGameManager.hasGame: : invalid param")
            return False
            pass
        return True
