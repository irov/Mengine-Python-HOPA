from Foundation.DatabaseManager import DatabaseManager

class ConnectorsManager(object):
    s_games = {}

    class ConnectorsGame(object):
        def __init__(self, elements, connections):
            self.elements = elements
            self.connections = connections
            pass
        pass

    class Connection(object):
        def __init__(self, socketName, statesName):
            self.socketObjectName = socketName
            self.statesObjectName = statesName
            self.elements = []
            pass

        def appendElements(self, element):
            self.elements.appned(element)
            pass
        pass

    @staticmethod
    def loadGames(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            Name = record.get("Name")
            ElementsParam = record.get("Elements")
            ConnectionsParam = record.get("Connections")
            ElementsToConnectionParam = record.get("ElementsToConnection")

            ConnectorsManager.loadGame(Name, module, ElementsParam, ConnectionsParam, ElementsToConnectionParam)
            pass
        pass

    @staticmethod
    def loadGame(name, module, elementsParam, connectionsParam, elementsToConnectionParam):
        elements = ConnectorsManager.loadGameElements(module, elementsParam)
        connections = ConnectorsManager.loadGameConnections(module, connectionsParam)
        ConnectorsManager.loadGameElementsToConnection(module, elementsToConnectionParam)

        game = ConnectorsManager.ConnectorsGame(elements, connections)
        ConnectorsManager.s_games[name] = game
        return game
        pass

    @staticmethod
    def loadGameElements(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        elements = {}
        for record in records:
            elementId = record.get("ElementId")
            objectName = record.get("ObjectName")
            needCount = record.get("NeedCount")

            elements[elementId] = dict(ObjectName=objectName, NeedCount=needCount)
            pass

        return elements
        pass

    @staticmethod
    def loadGameConnections(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        connections = {}
        for record in records:
            ConnectionId = record.get("ConnectionId")
            SocketObjectName = record.get("SocketObjectName")
            StatesObjectName = record.get("StatesObjectName")

            connection = ConnectorsManager.Connection(SocketObjectName, StatesObjectName)
            connections[ConnectionId] = connection
            pass

        return connections
        pass

    @staticmethod
    def loadGameElementsToConnection(module, param, connections):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            ConnectionId = record.get("ConnectionId")
            ElementId = record.get("ElementId")
            if ConnectionId not in connections:
                Trace.log("Manager", 0, "ConnectorsManager.loadGameElementsToConnection: invalid ConnectionId %i" % (ConnectionId))
                pass

            connection = connections[ConnectionId]
            connection.appendElements(ElementId)
            pass
        pass

    @staticmethod
    def getGame(name):
        if name not in ConnectorsManager.s_games:
            return None
            pass
        game = ConnectorsManager.s_games[name]
        return game
        pass

    @staticmethod
    def hasGame(name):
        return name in ConnectorsManager.s_games
        pass

    pass