from Foundation.DatabaseManager import DatabaseManager
from Foundation.Manager import Manager


class LampOnCursorManager(Manager):
    s_scenes = []

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            SceneName = record.get("SceneName")

            if SceneName is None:
                continue

            LampOnCursorManager.s_scenes.append(SceneName)

        return True
        pass

    @staticmethod
    def isLampOnCursorScene(SceneName):
        return SceneName in LampOnCursorManager.s_scenes
