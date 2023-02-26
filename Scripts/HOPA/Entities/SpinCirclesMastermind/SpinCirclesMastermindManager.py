import Trace
from Foundation.DatabaseManager import DatabaseManager

class SpinCirclesMastermindManager(object):
    s_objects = {}

    class MastermindData(object):
        def __init__(self, relatedSpinCirclesName, TriggerName, BullsCollection, CowsCollection, size):
            self.spinName = relatedSpinCirclesName
            self.triggerName = TriggerName
            self.bullsCollection = BullsCollection
            self.cowsCollection = CowsCollection
            self.gameSize = size
            pass

        def getSpinName(self):
            return self.spinName
            pass

        def getTriggerName(self):
            return self.triggerName
            pass

        def getBulls(self):
            return self.bullsCollection
            pass

        def getCows(self):
            return self.cowsCollection
            pass

        def getSize(self):
            return self.gameSize
            pass
        pass

    @staticmethod
    def onFinalize():
        SpinCirclesMastermindManager.s_objects = {}
        pass

    @staticmethod
    def loadSpinCirclesMastermind(module, name):
        records = DatabaseManager.getDatabaseRecords(module, name)

        for values in records:
            enigmaName = values.get("Name")
            relatedSpinCirclesName = values.get("RelatedSpinCircles")
            TriggerName = values.get("Trigger")
            BullsCollectionParam = values.get("BullsCollection")
            CowsCollectionParam = values.get("CowsCollection")
            WinParam = values.get("Size")

            BullsCollection = SpinCirclesMastermindManager.loadBullsCollection(module, BullsCollectionParam)
            CowsCollection = SpinCirclesMastermindManager.loadCowsCollection(module, CowsCollectionParam)

            object = SpinCirclesMastermindManager.MastermindData(relatedSpinCirclesName, TriggerName, BullsCollection, CowsCollection, WinParam)
            SpinCirclesMastermindManager.s_objects[enigmaName] = object
            pass
        pass

    @staticmethod
    def loadBullsCollection(module, collectionParam):
        records = DatabaseManager.getDatabaseRecords(module, collectionParam)
        bullsCollection = {}

        for values in records:
            Value = values.get("Value")
            MovieName = values.get("MovieName")
            bullsCollection[Value] = MovieName
            pass

        return bullsCollection
        pass

    @staticmethod
    def loadCowsCollection(module, collectionParam):
        records = DatabaseManager.getDatabaseRecords(module, collectionParam)
        cowsCollection = {}

        for values in records:
            Value = values.get("Value")
            MovieName = values.get("MovieName")
            cowsCollection[Value] = MovieName
            pass

        return cowsCollection
        pass

    @staticmethod
    def getSpinCirclesMastermind(name):
        if SpinCirclesMastermindManager.hasMastermind(name) is False:
            return None
            pass
        record = SpinCirclesMastermindManager.s_objects[name]
        return record
        pass

    @staticmethod
    def hasMastermind(name):
        if name not in SpinCirclesMastermindManager.s_objects:
            Trace.log("SpinCirclesMastermindManager", 0, "SpinCirclesMastermindManager.hasMastermind: : invalid param")
            return False
            pass
        return True
        pass

    pass

pass