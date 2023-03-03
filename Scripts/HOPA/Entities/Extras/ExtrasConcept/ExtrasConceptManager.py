from Foundation.DatabaseManager import DatabaseManager


class ExtrasConceptManager(object):
    s_data = []

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            spriteName = record.get("SpriteName")

            ExtrasConceptManager.s_data.append(spriteName)
            pass

    @staticmethod
    def getData():
        return ExtrasConceptManager.s_data
        pass

    pass
