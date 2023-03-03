from Foundation.DatabaseManager import DatabaseManager
from Foundation.GroupManager import GroupManager


class StrategyGuideControllerManager(object):
    s_pages = {}

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            pageID = record.get("PageID")
            groupName = record.get("GroupName")
            objectName = record.get("ObjectName")

            object = GroupManager.getObject(groupName, objectName)

            StrategyGuideControllerManager.s_pages[pageID] = object
            pass

        pass

    @staticmethod
    def getPages():
        return StrategyGuideControllerManager.s_pages
        pass

    pass
