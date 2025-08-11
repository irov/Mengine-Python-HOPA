from Foundation.Manager import Manager

from Foundation.DatabaseManager import DatabaseManager

class LocationCompleteManager(Manager):
    s_questTypeFilter = []

    @staticmethod
    def _onFinalize():
        LocationCompleteManager.s_questTypeFilter = []
        pass

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            IgnoredQuestType = record.get("IgnoredQuestType")
            LocationCompleteManager.s_questTypeFilter.append(IgnoredQuestType)

        return True

    @staticmethod
    def hasQuestTypeFilter():
        if len(LocationCompleteManager.s_questTypeFilter) == 0:
            return False

        return True

    @staticmethod
    def getQuestTypeFilter():
        return LocationCompleteManager.s_questTypeFilter
