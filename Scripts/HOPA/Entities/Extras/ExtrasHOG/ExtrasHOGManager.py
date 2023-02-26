from Foundation.DatabaseManager import DatabaseManager

class ExtrasHOGManager(object):
    s_data = {}

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            spriteName = record.get("SpriteName")
            SceneName = record.get("SceneName")
            ScenarioID = record.get("ScenarioID")

            ExtrasHOGManager.s_data[spriteName] = (SceneName, ScenarioID)
            pass
        pass

    @staticmethod
    def getData():
        return ExtrasHOGManager.s_data
        pass

    pass