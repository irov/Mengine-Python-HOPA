import Trace
from Foundation.DatabaseManager import DatabaseManager

class ButtonConjunctionManager(object):
    TraceName = "ButtonConjunctionManager"
    s_objects = {}

    class ButtonCollection(object):
        def __init__(self, movieActive, movieDown, movieOver, sockets):
            self.moviesActive = movieActive
            self.moviesDown = movieDown
            self.moviesOver = movieOver
            self.sockets = sockets
            pass

        def getSockets(self):
            return self.sockets
            pass

        def getMoviesActive(self):
            return self.moviesActive
            pass

        def getMoviesDown(self):
            return self.moviesDown
            pass

        def getMoviesOver(self):
            return self.moviesOver
            pass

        def __repr__(self):
            return self.__dict__.__repr__()
            pass

    @staticmethod
    def onFinalize():
        ButtonConjunctionManager.s_objects = {}
        pass

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for values in records:
            objectName = values.get("EnigmaName")
            if objectName == "":
                continue
            collectionName = values.get("Collection")
            ButtonConjunctionManager.loadCollection(objectName, collectionName)
            pass
        pass

    @staticmethod
    def loadCollection(enigmaName, module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)
        moviesActive = [map.get("MovieActive") for map in records]
        moviesDown = [map.get("MovieDown") for map in records]
        moviesOver = [map.get("MovieOver") for map in records]
        sockets = [map.get("Socket") for map in records]
        associationInstance = ButtonConjunctionManager.ButtonCollection(moviesActive, moviesDown, moviesOver, sockets)
        ButtonConjunctionManager.s_objects[enigmaName] = associationInstance
        #        print associationInstance  # repr
        pass

    @staticmethod
    def getCollection(name):
        if name not in ButtonConjunctionManager.s_objects.keys():
            Trace.log(ButtonConjunctionManager.TraceName, 0, "%s.getCollection: cant find %s" % (ButtonConjunctionManager.TraceName, name))
            return None
            pass
        collection = ButtonConjunctionManager.s_objects[name]
        return collection
        pass

    @staticmethod
    def hasCollection(name):
        if name not in ButtonConjunctionManager.s_objects.keys():
            return False
            pass
        return True
        pass