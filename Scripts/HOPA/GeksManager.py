from Foundation.Manager import Manager

from Foundation.DatabaseManager import DatabaseManager
from HOPA.EnigmaManager import EnigmaManager


class GeksManager(Manager):
    s_objects = {}

    class Geks(object):
        def __init__(self, enigmaObject, listButtons, listAllButtons, sceneName):
            self.enigmaObject = enigmaObject
            self.listButtons = listButtons
            self.listAllButtons = listAllButtons
            self.sceneName = sceneName

    @staticmethod
    def _onFinalize():
        GeksManager.s_objects = {}
        pass

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            enigmaName = record.get("Name")
            collectionName = record.get("GeksCollection")
            levelsName = record.get("GeksLevels")

            sceneName = EnigmaManager.getEnigmaSceneName(collectionName)

            GeksManager.loadGeksCollection(enigmaName, sceneName, module, collectionName, levelsName)

    @staticmethod
    def loadGeksCollection(enigmaName, sceneName, module, collectionName, levelsName):
        records = DatabaseManager.getDatabaseRecords(module, collectionName)

        listButtons = []
        listAllButtons = []

        EnigmaObject = EnigmaManager.getEnigmaObject(enigmaName)

        for record in records:
            buttons = record.get("Buttons")
            tempList = []
            for buttonName in buttons:
                button = EnigmaObject.getObject(buttonName)
                tempList.append(button)
                pass
            listButtons.append(tempList[:])
            pass

        records = DatabaseManager.getDatabaseRecords(module, levelsName)
        for record in records:
            buttons = record.get("Buttons")
            tempList = []
            for buttonName in buttons:
                button = EnigmaObject.getObject(buttonName)
                tempList.append(button)
                pass
            listAllButtons.append(tempList[:])
            pass

        Object = GeksManager.Geks(EnigmaObject, listButtons, listAllButtons, sceneName)

        GeksManager.s_objects[enigmaName] = Object

    @staticmethod
    def getGeks(name):
        if name not in GeksManager.s_objects.keys():
            return None
            pass

        return GeksManager.s_objects[name]
        pass

    @staticmethod
    def getEnigmaObject(name):
        if name not in GeksManager.s_objects.keys():
            return None
            pass

        return GeksManager.s_objects[name].enigmaObject
        pass

    @staticmethod
    def hasGeks(name):
        if name not in GeksManager.s_objects.keys():
            return False
            pass

        return True
