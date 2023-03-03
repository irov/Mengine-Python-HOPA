from Foundation.DatabaseManager import DatabaseManager


class SpinCirclesDependsPluginManager(object):
    s_objects = {}

    class DependData(object):
        def __init__(self, Depend, Direction, MovieName, L, R, InitValues):
            self.Depend = Depend
            self.Direction = Direction
            self.MovieName = MovieName
            self.OwnCheck = L
            self.dependCheck = R
            self.InitValues = InitValues
            pass

        def getDepend(self):
            return self.Depend
            pass

        def getDirection(self):
            return self.Direction
            pass

        def getMovieName(self):
            return self.MovieName
            pass

        def getL(self):
            return self.OwnCheck
            pass

        def getR(self):
            return self.dependCheck
            pass

        def getInitValues(self):
            return self.InitValues
            pass

        pass

    @staticmethod
    def onFinalize():
        SpinCirclesDependsPluginManager.s_objects = {}
        pass

    @staticmethod
    def loadParams(module, name):
        records = DatabaseManager.getDatabaseRecords(module, name)
        for value in records:
            name = value.get("Name")
            param = value.get("Param")
            depends = SpinCirclesDependsPluginManager.loadCollection(module, param)
            pass

        SpinCirclesDependsPluginManager.s_objects[name] = depends
        pass

    @staticmethod
    def loadCollection(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        depend = {}
        for value in records:
            Item = value.get("Item")
            Depend = value.get("Depend")
            Direction = value.get("Direction")
            MovieName = value.get("MovieName")
            L = value.get("L")
            R = value.get("R")
            InitValues = value.get("InitValues")

            data = SpinCirclesDependsPluginManager.DependData(Depend, Direction, MovieName, L, R, InitValues)
            depend[Item] = data
            pass

        return depend
        pass

    @staticmethod
    def getData(name):
        if SpinCirclesDependsPluginManager.hasData(name) is False:
            return None
            pass
        record = SpinCirclesDependsPluginManager.s_objects[name]
        return record
        pass

    @staticmethod
    def hasData(name):
        if name not in SpinCirclesDependsPluginManager.s_objects:
            Trace.log("SpinCirclesDependsPluginManager", 0,
                      "SpinCirclesDependsPluginManager.hasData invalid param name %s" % (name))
            return False
            pass
        return True
        pass

    pass
