from Foundation.Manager import Manager

from Foundation.DatabaseManager import DatabaseManager
from Foundation.GroupManager import GroupManager

class StrategyGuideZoomManager(Manager):
    s_objects = {}

    @staticmethod
    def _onFinalize():
        StrategyGuideZoomManager.s_objects = {}
        pass

    @staticmethod
    def loadParams(module, Param):
        records = DatabaseManager.getDatabaseRecords(module, Param)

        for record in records:
            PageGroupName = record.get("PageGroupName")
            DemonName = record.get("DemonName")
            SocketName = record.get("SocketName")
            groupName = record.get("GroupName")
            objectName = record.get("ObjectName")

            demon = GroupManager.getObject(PageGroupName, DemonName)
            socket = demon.getObject(SocketName)
            object = GroupManager.getObject(groupName, objectName)

            StrategyGuideZoomManager.s_objects[socket] = object
            pass
        pass

    @staticmethod
    def getZooms():
        return StrategyGuideZoomManager.s_objects
