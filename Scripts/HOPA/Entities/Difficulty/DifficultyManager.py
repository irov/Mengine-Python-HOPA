from Foundation.Manager import Manager

from Foundation.DatabaseManager import DatabaseManager
from Foundation.GroupManager import GroupManager


class DifficultyManager(Manager):
    s_difficulties = {}

    @staticmethod
    def _onFinalize():
        DifficultyManager.s_difficulties = {}
        pass

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            id = record.get("ID")

            selectGroupName = record.get("SelectGroupName")
            selectObjectName = record.get("SelectObjectName")

            selectObject = GroupManager.getObject(selectGroupName, selectObjectName)

            DifficultyManager.s_difficulties[id] = selectObject
            pass

        return True
        pass

    @staticmethod
    def getDifficulties():
        if len(DifficultyManager.s_difficulties) == 0:
            Trace.log("Manager", 0, "DifficultyManager.getDifficulties: s_difficulties is empty")
            return None
            pass

        return DifficultyManager.s_difficulties
