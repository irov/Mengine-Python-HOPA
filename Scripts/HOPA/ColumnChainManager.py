from Foundation.Manager import Manager

from Foundation.DatabaseManager import DatabaseManager

class ColumnChainManager(Manager):
    s_objects = {}

    class ColumnChain(object):
        def __init__(self, columnBySocket):  # all args are list except first
            self.columnBySocket = columnBySocket
            pass

        def getColumnBySocket(self):
            return self.columnBySocket

    class Column(object):
        def __init__(self, columnName, startState, statesLength, winState, movieObjectNameList):
            self.columnName = columnName
            self.startState = startState
            self.statesLength = statesLength
            self.winState = winState
            self.movieObjectNameList = movieObjectNameList
            pass

        def getColumnName(self):
            return self.columnName

        def getStartState(self):
            return self.startState

        def getStatesLength(self):
            return self.statesLength

        def getWinState(self):
            return self.winState

        def getMovieObjectNameList(self):
            return self.movieObjectNameList

    @staticmethod
    def _onFinalize():
        ColumnChainManager.s_objects = {}
        pass

    @staticmethod
    def loadParams(module, name):
        records = DatabaseManager.getDatabaseRecords(module, name)

        for values in records:
            enigmaName = values.get("Name")
            collectionParam = values.get("Collection")
            ColumnChainManager.loadColumnChainCollection(module,enigmaName, collectionParam)

    @staticmethod
    def loadColumnChainCollection(module, enigmaName, collectionParam):
        records = DatabaseManager.getDatabaseRecords(module, collectionParam)

        ColumnsBySocket = {}
        for values in records:
            ColumnName = values.get("ColumnName")
            ColumnSocketObjectName = values.get("SocketObjectName")
            ColumnStartState = values.get("StartState")
            ColumnStatesLength = values.get("StatesLength")
            ColumnWinState = values.get("WinState")
            ColumnMovieObjectNameList = values.get("MovieObjectNames")

            column = ColumnChainManager.Column(ColumnName, ColumnStartState, ColumnStatesLength, ColumnWinState,
                                               ColumnMovieObjectNameList)
            ColumnsBySocket[ColumnSocketObjectName] = column
            pass

        game = ColumnChainManager.ColumnChain(ColumnsBySocket)
        ColumnChainManager.s_objects[enigmaName] = game
        pass

    @staticmethod
    def getColumnChain(name):
        if ColumnChainManager.hasColumnChain(name) is False:
            return None
            pass
        record = ColumnChainManager.s_objects[name]
        return record
        pass

    @staticmethod
    def hasColumnChain(name):
        if name not in ColumnChainManager.s_objects:
            Trace.log("ColumnChainManager", 0, "ColumnChainManager.hasColumnChain: : invalid param")
            return False
            pass
        return True
