from Foundation.Manager import Manager
from Foundation.DatabaseManager import DatabaseManager
from Foundation.GroupManager import GroupManager

class ArrowBlackListManager(Manager):
    s_ignores = {}

    class Ignored(object):
        def __init__(self, changeType, socketName):
            self.changeType = changeType
            self.socketName = socketName

        def getChangeType(self):
            return self.changeType

        def getSocketName(self):
            return self.socketName

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            groupName = record["Group"]
            name = record["Name"]
            changeType = record.get("ChangeType", "Default")
            DemonName = record.get("DemonName", None)
            SocketName = record.get("SocketName", None)

            group = GroupManager.getGroup(groupName)
            if isinstance(group, GroupManager.EmptyGroup):
                continue

            if DemonName is None:
                object = GroupManager.getObject(groupName, name)
            else:
                demon = GroupManager.getObject(groupName, DemonName)
                object = demon.getObject(name)

            Ignored = ArrowBlackListManager.Ignored(changeType, SocketName)
            ArrowBlackListManager.s_ignores[object] = Ignored

        return True

    @staticmethod
    def isIgnore(object):
        return object in ArrowBlackListManager.s_ignores.keys()

    @staticmethod
    def getChangeType(object):
        data = ArrowBlackListManager.getIgnored(object)
        changeType = data.getChangeType()
        return changeType

    @staticmethod
    def getIgnored(object):
        return ArrowBlackListManager.s_ignores[object]