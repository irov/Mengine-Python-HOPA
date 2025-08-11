from Foundation.Manager import Manager

from Foundation.DatabaseManager import DatabaseManager
from Foundation.GroupManager import GroupManager


class CollectedMapManager(Manager):
    s_objects = {}
    s_partsRelation = {}

    class Data(object):
        pass

    @staticmethod
    def _onFinalize():
        CollectedMapManager.s_objects = {}
        CollectedMapManager.s_partsRelation = {}
        pass

    @staticmethod
    def loadData(module, name):
        records = DatabaseManager.getDatabaseRecords(module, name)

        for record in records:
            DemonName = record.get("DemonName")
            GroupName = record.get("GroupName")
            CollectionParam = record.get("ValuesCollection")

            Demon = GroupManager.getObject(GroupName, DemonName)
            values = CollectedMapManager.loadCollection(module, CollectionParam, Demon)

            CollectedMapManager.s_objects[Demon] = values
            pass
        pass

    @staticmethod
    def loadCollection(module, param, demon):
        records = DatabaseManager.getDatabaseRecords(module, param)
        values = {}

        for record in records:
            ID = record.get("PartID")
            ObjectName = record.get("ObjectName")

            Object = demon.getObject(ObjectName)

            values[ID] = Object
            CollectedMapManager.s_partsRelation[ID] = demon
            pass
        return values
        pass

    @staticmethod
    def getData(demon):
        if CollectedMapManager.hasData(demon) is False:
            return None
            pass
        record = CollectedMapManager.s_objects[demon]
        return record
        pass

    @staticmethod
    def hasData(demon):
        if demon not in CollectedMapManager.s_objects:
            Trace.log("CollectedMapManager", 0,
                      "CollectedMapManager.hasData invalid param demon %s" % (demon.getName()))
            return False
            pass
        return True
        pass

    @staticmethod
    def getObjectByPart(partID):
        return CollectedMapManager.s_partsRelation[partID]
        pass

    pass
