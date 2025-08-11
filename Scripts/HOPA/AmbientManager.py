from Foundation.Manager import Manager

from Foundation.DatabaseManager import DatabaseManager

from Foundation.GroupManager import GroupManager

class AmbientManager(Manager):
    s_ambients = {}

    @staticmethod
    def _onInitialize():
        pass

    @staticmethod
    def _onFinalize():
        AmbientManager.s_ambients = {}
        pass

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            SceneName = record.get("SceneName")
            AmbientGroup = record.get("AmbientGroup")
            SwitchName = record.get("SwitchName")
            AmbientName = record.get("AmbientName")

            Demon_Switch = GroupManager.getObject(AmbientGroup, SwitchName)

            AmbientManager.addAmbient(SceneName, Demon_Switch, AmbientName)
            pass
        pass

    @staticmethod
    def addAmbient(sceneName, demonSwitch, ambientName):
        AmbientManager.s_ambients[sceneName] = (demonSwitch, ambientName)
        pass

    @staticmethod
    def hasAmbient(sceneName):
        return sceneName in AmbientManager.s_ambients

    @staticmethod
    def getAmbients():
        return AmbientManager.s_ambients

    @staticmethod
    def getAmbient(sceneName):
        return AmbientManager.s_ambients[sceneName]
