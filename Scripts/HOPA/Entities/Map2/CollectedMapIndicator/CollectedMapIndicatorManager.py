from Foundation.DatabaseManager import DatabaseManager
from Foundation.GroupManager import GroupManager

class CollectedMapIndicatorManager(object):
    s_objects = {}

    @staticmethod
    def loadCollectedMapIndicator(module, name):
        records = DatabaseManager.getDatabaseRecords(module, name)

        for values in records:
            DemonName = values.get("DemonName")
            GroupName = values.get("GroupName")

            object = GroupManager.getObject(GroupName, DemonName)

            ValuesCollectionParam = values.get("ValuesCollection")
            objectValues = CollectedMapIndicatorManager.loadValues(module, ValuesCollectionParam, object)

            CollectedMapIndicatorManager.s_objects[DemonName] = objectValues
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
    def getData(demonName):
        if CollectedMapIndicatorManager.hasData(demonName) is False:
            return None
            pass
        record = CollectedMapIndicatorManager.s_objects[demonName]
        return record
        pass

    @staticmethod
    def hasData(demonName):
        if demonName not in CollectedMapIndicatorManager.s_objects:
            Trace.log("CollectedMapIndicatorManager", 0, "CollectedMapIndicatorManager.hasData invalid param demonName %s" % (demonName))
            return False
            pass
        return True
        pass

    @staticmethod
    def getCurrentValueMovie(demonName, value):
        if CollectedMapIndicatorManager.hasData(demonName) is False:
            Trace.log("CollectedMapIndicator", 0, "CollectedMapIndicatorManager.getCurrentValueMovie invalid params demonName::%s" % (demonName,))
            return None
            pass
        values = CollectedMapIndicatorManager.s_objects[demonName]
        if value not in values:
            return None
            pass
        movie = values[value]
        return movie
        pass

    pass