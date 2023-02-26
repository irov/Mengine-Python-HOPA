from Foundation.DatabaseManager import DatabaseManager
from Foundation.GroupManager import GroupManager

class CollectedAmuletManager(object):
    s_objects = {}

    class CollectedAmuletData(object):
        def __init__(self, states, values, socket):
            self.states = states
            self.values = values
            self.socket = socket
            pass

        def getStates(self):
            return self.states
            pass

        def getValues(self):
            return self.values
            pass

        def getState(self, state):
            return self.states[state]
            pass

        def getValue(self, value):
            return self.values[value]
            pass

        def getSocket(self):
            return self.socket
            pass
        pass

    @staticmethod
    def _onFinalize():
        CollectedAmuletManager.s_objects = {}
        pass

    @staticmethod
    def loadCollectedAmuletData(module, name):
        records = DatabaseManager.getDatabaseRecords(module, name)

        for value in records:
            GroupName = value.get("GroupName")
            ObjectName = value.get("ObjectName")
            ValuesCollectionParam = value.get("ValuesCollection")
            StatesCollectionParam = value.get("StatesCollection")
            SocketName = value.get("SocketName")

            demon = GroupManager.getObject(GroupName, ObjectName)
            values = CollectedAmuletManager.loadValues(module, ValuesCollectionParam, demon)
            states = CollectedAmuletManager.loadStates(module, StatesCollectionParam, demon)
            socket = demon.getObject(SocketName)

            data = CollectedAmuletManager.CollectedAmuletData(states, values, socket)

            CollectedAmuletManager.s_objects[demon] = data
            pass
        pass

    @staticmethod
    def loadValues(module, param, demon):
        records = DatabaseManager.getDatabaseRecords(module, param)
        values = {}
        for record in records:
            Value = record.get("Value")
            MovieName = record.get("MovieName")
            movie = demon.getObject(MovieName)
            values[Value] = movie
            pass
        return values
        pass

    @staticmethod
    def loadStates(module, param, demon):
        records = DatabaseManager.getDatabaseRecords(module, param)
        states = {}
        for record in records:
            Value = record.get("State")
            MovieName = record.get("MovieName")
            movie = demon.getObject(MovieName)
            states[Value] = movie
            pass
        return states
        pass

    @staticmethod
    def getData(obj):
        if CollectedAmuletManager.hasData(obj) is False:
            return None
            pass
        record = CollectedAmuletManager.s_objects[obj]
        return record
        pass

    @staticmethod
    def hasData(obj):
        if obj not in CollectedAmuletManager.s_objects:
            Trace.log("CollectedAmuletManager", 0, "CollectedAmuletManager.hasData invalid param obj %s" % (obj))
            return False
            pass
        return True
        pass

    pass