from Foundation.Manager import Manager

from Foundation.DatabaseManager import DatabaseManager

class SplashScreenManager(Manager):
    databaseORMs = []

    @staticmethod
    def _onFinalize():
        SplashScreenManager.databaseORMs = []
        pass

    @staticmethod
    def loadParams(module, param):
        SplashScreenManager.databaseORMs = DatabaseManager.getDatabaseORMs(module, param)

        return True

    @staticmethod
    def getSplashScreenData():
        return SplashScreenManager.databaseORMs

    pass
