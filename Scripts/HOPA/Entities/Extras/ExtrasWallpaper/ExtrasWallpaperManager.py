from Foundation.Manager import Manager

from Foundation.DatabaseManager import DatabaseManager

class ExtrasWallpaperManager(Manager):
    s_data = {}

    @staticmethod
    def _onFinalize():
        ExtrasWallpaperManager.s_data = {}
        pass

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            spriteName = record.get("SpriteName")
            resourceName = record.get("ResourceName")
            FileName = record.get("FileName")

            ExtrasWallpaperManager.s_data[spriteName] = (resourceName, FileName)
            pass

    @staticmethod
    def getData():
        return ExtrasWallpaperManager.s_data
        pass

    pass
