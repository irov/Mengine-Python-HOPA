from Foundation.Manager import Manager

from Foundation.DatabaseManager import DatabaseManager
from Foundation.GroupManager import GroupManager


class MapSwitchManager(Manager):
    s_objects = {}

    @staticmethod
    def _onFinalize():
        MapSwitchManager.s_objects = {}
        pass

    @staticmethod
    def loadData(module, name):
        records = DatabaseManager.getDatabaseRecords(module, name)

        for record in records:
            DemonName = record.get("DemonName")
            GroupName = record.get("GroupName")

            demon = GroupManager.getObject(GroupName, DemonName)

            CollectionParam = record.get("Collection")

            data = MapSwitchManager.loadCollection(module, CollectionParam, demon)

            MapSwitchManager.s_objects[demon] = data

    @staticmethod
    def loadCollection(module, CollectionParam, demon):
        data = {}
        records = DatabaseManager.getDatabaseRecords(module, CollectionParam)

        for record in records:
            ButtonName = record.get("ButtonName")
            SceneName = record.get("SceneName")

            button = demon.getObject(ButtonName)

            data[button] = SceneName
            pass

        return data
        pass

    @staticmethod
    def getData(demon):
        if MapSwitchManager.hasData(demon) is False:
            return None
            pass
        record = MapSwitchManager.s_objects[demon]
        return record
        pass

    @staticmethod
    def hasData(demon):
        if demon not in MapSwitchManager.s_objects:
            Trace.log("MapSwitchManager", 0, "MapSwitchManager.hasData invalid param for demon %s" % (demon.getName()))
            return False
        return True
