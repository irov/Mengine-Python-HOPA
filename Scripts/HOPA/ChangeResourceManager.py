from Foundation.DatabaseManager import DatabaseManager
from Foundation.GroupManager import GroupManager

class ChangeResourceManager(object):

    @staticmethod
    def loadObjects(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            GroupName = record.get("GroupName")
            ObjectName = record.get("ObjectName")
            NewImageResource = record.get("NewImageResource")

            object = GroupManager.getObject(GroupName, ObjectName)
            object.setParam("ExtraResource", NewImageResource)
            pass
        pass
    pass