from Foundation.DatabaseManager import DatabaseManager


class SplashScreenManager(object):
    databaseORMs = []

    @staticmethod
    def loadParams(module, param):
        SplashScreenManager.databaseORMs = DatabaseManager.getDatabaseORMs(module, param)

        return True
        pass

    @staticmethod
    def getSplashScreenData():
        return SplashScreenManager.databaseORMs
        pass

    pass
