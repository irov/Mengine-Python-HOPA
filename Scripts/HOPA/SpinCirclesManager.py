from Foundation.Manager import Manager

from Foundation.DatabaseManager import DatabaseManager
from HOPA.EnigmaManager import EnigmaManager

class SpinCirclesManager(Manager):
    s_objects = {}

    class SpinCircle(object):
        def __init__(self, params):  # all args are list except first
            self.params = params
            pass

        def getEnigmaObject(self):
            return self.params[0]

        def getParams(self):
            return self.params

    @staticmethod
    def _onFinalize():
        SpinCirclesManager.s_objects = {}
        pass

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for values in records:
            objectName = values.get("Name")
            if objectName == "":
                continue

            collectionName = values.get("Collection")

            isHold = bool(values.get("isHold", 1))
            SpinCirclesManager.loadSpinCircleCollection(objectName, module, collectionName, isHold)
            pass

        return True
        pass

    @staticmethod
    def loadSpinCircleCollection(objectName, module, param, isHold):
        records = DatabaseManager.getDatabaseRecords(module, param)
        EnigmaObject = EnigmaManager.getEnigmaObject(objectName)

        ItemList = []
        DependsList = []
        FinalStateList = []
        DependRotateList = []
        MovieList = []
        MovieListRevert = []
        Indicators = []
        Overs = []
        MultiFinalStateMap = {}

        for values in records:
            RotateItem = values.get("RotateItem")
            if RotateItem == "":
                continue
            direction = values.get("Direction", "L")

            if (direction == "L"):
                ItemList.append(RotateItem)
                RotateInDepends = values.get("RotateInDepends")
                DependsList.append(RotateInDepends)

                DependRotate = values.get("DependRotate")
                DependRotateList.append(DependRotate)
                FinalState = values.get("FinalState")

                multi_key = (RotateItem, DependRotate)
                if multi_key in MultiFinalStateMap:  # tricky
                    link_to_list = MultiFinalStateMap[multi_key]
                    link_to_list.append(FinalState)
                    pass
                else:
                    sub_list = [FinalState]
                    FinalStateList.append(sub_list)
                    MultiFinalStateMap[multi_key] = sub_list
                    pass

                Indicator = values.get("Indicators")
                Indicators.append(Indicator)
                MovieName = values.get("Movies")
                MovieList.append(MovieName)
                MovieListRevert.append([])
                Over = values.get("onEnterSocket")
                if Over is not None:
                    Overs.append(Over)
                    pass
                pass
            elif (direction == "R"):
                MovieName = values.get("Movies")
                for id, it in enumerate(ItemList):
                    if (it == RotateItem):
                        MovieListRevert[id] = MovieName
                        break
                        pass
                    pass
                pass
            pass

        params = [EnigmaObject, ItemList, DependsList, FinalStateList, DependRotateList, Indicators, MovieList, MovieListRevert, Overs, isHold]
        Object = SpinCirclesManager.SpinCircle(params)

        SpinCirclesManager.s_objects[objectName] = Object

        pass

    @staticmethod
    def getSpinCircle(name):
        if not SpinCirclesManager.hasSpinCircle(name):
            return None
            pass
        record = SpinCirclesManager.s_objects[name]
        return record
        pass

    @staticmethod
    def getEnigmaObject(name):
        if not SpinCirclesManager.hasSpinCircle(name):
            return None
            pass
        record = SpinCirclesManager.s_objects[name]
        return record.getEnigmaObject()
        pass

    @staticmethod
    def hasSpinCircle(name):
        if name not in SpinCirclesManager.s_objects:
            Trace.log("SpinCirclesManager", 0, "SpinSirclesManager.hasSpinCircle: : invalid param")
            return False
            pass
        return True
        pass

    @staticmethod
    def getParams(name):
        if not SpinCirclesManager.hasSpinCircle(name):
            return None
            pass
        record = SpinCirclesManager.s_objects[name]
        return record.getParams()
