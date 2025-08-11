from Foundation.Manager import Manager

from Foundation.DatabaseManager import DatabaseManager
from Foundation.GroupManager import GroupManager

class StrategyGuidePageManager(Manager):
    s_objects = {}

    @staticmethod
    def _onFinalize():
        StrategyGuidePageManager.s_objects = {}
        pass

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            PageGroupName = record.get("PageGroupName")
            DemonName = record.get("DemonName")
            SocketName = record.get("SocketName")

            demon = GroupManager.getObject(PageGroupName, DemonName)
            socket = demon.getObject(SocketName)

            arr = StrategyGuidePageManager.s_objects.setdefault(demon, [])
            arr.append(socket)
            pass
        pass

    @staticmethod
    def getSockets(demon):
        if StrategyGuidePageManager.hasSockets(demon) is False:
            Trace.log("StrategyGuidePageManager", 0,
                      "StrategyGuidePageManager.getSockets invalid param demon %s" % (demon,))
            return None
        return StrategyGuidePageManager.s_objects[demon]

    @staticmethod
    def hasSockets(demon):
        if demon not in StrategyGuidePageManager.s_objects:
            return False
        return True
