import Trace
from Foundation.DatabaseManager import DatabaseManager

class AssociationElementsManager(object):
    TraceName = "AssociationElementsManager"
    s_objects = {}

    class AssociationCollection(object):
        def __init__(self, movieList, slots):
            self.movies = movieList
            self.slots = slots
            pass

        def getSlots(self):
            return self.slots
            pass

        def getMovies(self):
            return self.movies

        def __repr__(self):
            return self.__dict__.__repr__()
            pass

    @staticmethod
    def onFinalize():
        AssociationElementsManager.s_objects = {}
        pass

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for values in records:
            objectName = values.get("EnigmaName")
            if objectName == "":
                continue
            collectionName = values.get("Collection")
            AssociationElementsManager.loadCollection(objectName, collectionName)
            pass
        pass

    @staticmethod
    def loadCollection(module, enigmaName, param):
        records = DatabaseManager.getDatabaseRecords(module, param)
        movieList = [map.get("MovieName") for map in records]
        slotList = [map.get("SlotNames") for map in records]
        associationInstance = AssociationElementsManager.AssociationCollection(movieList, slotList)
        AssociationElementsManager.s_objects[enigmaName] = associationInstance
        #        print associationInstance  # repr
        pass

    @staticmethod
    def getCollection(name):
        if name not in AssociationElementsManager.s_objects.keys():
            Trace.log(AssociationElementsManager.TraceName, 0, "%s.getCollection: cant find %s" % (AssociationElementsManager.TraceName, name))
            return None
            pass
        collection = AssociationElementsManager.s_objects[name]
        return collection
        pass

    @staticmethod
    def hasCollection(name):
        if name not in AssociationElementsManager.s_objects.keys():
            return False
            pass
        return True
        pass