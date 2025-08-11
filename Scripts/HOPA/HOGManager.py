from Foundation.Manager import Manager

from Foundation.DatabaseManager import DatabaseManager
from Foundation.DemonManager import DemonManager
from HOPA.EnigmaManager import EnigmaManager


class HOGManager(Manager):
    s_hogs = {}
    s_hogTypes = {}

    class HOG(object):
        def __init__(self, paramType, sceneName, objectHOG):
            self.paramType = paramType
            self.sceneName = sceneName
            self.objectHOG = objectHOG

    @staticmethod
    def _onInitialize():
        pass

    @staticmethod
    def _onFinalize():
        HOGManager.s_hogs = {}
        HOGManager.s_hogTypes = {}
        pass

    @staticmethod
    def importParamTypes(module, listTypes):
        for typeName in listTypes:
            HOGManager.importParamType(module, typeName)

    @staticmethod
    def importParamType(module, name):
        Name = "%s" % (name)
        FromName = module
        ModuleName = "%s.%s" % (FromName, Name)
        Module = __import__(ModuleName, fromlist=[FromName])
        Type = getattr(Module, Name)
        HOGManager.addParamType(name, Type)

    @staticmethod
    def addParamType(name, param):
        HOGManager.s_hogTypes[name] = param

    @staticmethod
    def getParamType(type):
        param = HOGManager.s_hogTypes[type]
        return param

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            Name = record.get("Name")
            ParamType = record.get("Type", "HOGParamDefault")
            Param = record.get("Param")
            Inventory = record.get("Inventory")
            if Inventory is not None:
                param = HOGManager.getParamType(ParamType)
                inventory = DemonManager.getDemon(Inventory)
                param.setInventory(Name, inventory)

            HOGManager.loadHOG(module, Name, ParamType, Param)

        return True

    @staticmethod
    def loadHOG(module, name, paramType, param):
        if EnigmaManager.hasEnigma(name) is False:
            return False

        objectHOG = EnigmaManager.getEnigmaObject(name)

        sceneName = EnigmaManager.getEnigmaSceneName(name)

        Param = HOGManager.getParamType(paramType)
        if Param.loadHOGItems(module, param, name) is False:
            return False
            pass

        hog = HOGManager.HOG(paramType, sceneName, objectHOG)
        HOGManager.addHOG(name, hog)
        pass

    @staticmethod
    def hasHOG(name):
        return name in HOGManager.s_hogs
        pass

    @staticmethod
    def getHOG(name):
        if name not in HOGManager.s_hogs:
            Trace.log("HOGManager", 0, "HOGManager.getHOG: not found hog %s" % name)
            return None
            pass

        hog = HOGManager.s_hogs[name]

        return hog
        pass

    @staticmethod
    def getInventory(name):
        hog = HOGManager.getHOG(name)
        param = HOGManager.getParamType(hog.paramType)
        inventory = param.getInventory(name)
        return inventory
        pass

    @staticmethod
    def setInventory(name, inventory):
        hog = HOGManager.getHOG(name)
        param = HOGManager.getParamType(hog.paramType)
        param.setInventory(name, inventory)
        pass

    @staticmethod
    def getHOGItems(name):
        if HOGManager.hasHOG(name) is False:
            Trace.log("HOGManager", 0, "HOGManager.getHOGItems: not found hog %s" % (name))
            return None
            pass

        hog = HOGManager.getHOG(name)
        param = HOGManager.getParamType(hog.paramType)

        items = param.getHOGItems(name)

        return items
        pass

    @staticmethod
    def getSceneHOGItems(name, sceneName):
        if HOGManager.hasHOG(name) is False:
            Trace.log("HOGManager", 0, "HOGManager.getSceneHOGItems: not found hog %s" % (name))
            return None
            pass

        hog = HOGManager.getHOG(name)
        param = HOGManager.getParamType(hog.paramType)

        items = param.getSceneHOGItems(sceneName)

        return items
        pass

    @staticmethod
    def getHOGItem(name, identity):
        if HOGManager.hasHOG(name) is False:
            Trace.log("HOGManager", 0, "HOGManager.getHOGItem: not found hog %s" % name)
            return None
            pass

        hog = HOGManager.getHOG(name)

        param = HOGManager.getParamType(hog.paramType)

        if param.hasHOGItem(name, identity) is False:
            Trace.log("HOGManager", 0, "HOGManager.getHOGItem: not found %s item %s" % (name, identity))
            return None
            pass

        item = param.getHOGItem(name, identity)

        return item
        pass

    @staticmethod
    def hasHOGItemTextID(name, identity):
        if HOGManager.hasHOG(name) is False:
            return False
            pass

        hog = HOGManager.getHOG(name)
        param = HOGManager.getParamType(hog.paramType)

        has = param.hasHOGItemTextID(name, identity)

        return has
        pass

    @staticmethod
    def filterCountItems(itemsList, enigmaName):
        newList = []
        tempDict = {}
        for name in itemsList:
            item = HOGManager.getHOGItem(enigmaName, name)
            itemTextID = item.getTextID()
            tempDict.setdefault(itemTextID, []).append(name)
            pass

        for listItems in tempDict.values():
            newList.append(listItems)
            pass

        return newList
        pass

    @staticmethod
    def getHOGItemTextID(name, identity):
        if HOGManager.hasHOG(name) is False:
            return None
            pass

        hog = HOGManager.getHOG(name)
        param = HOGManager.getParamType(hog.paramType)

        return param.getHOGItemTextID(name, identity)
        pass

    @staticmethod
    def getHOGObject(name):
        if HOGManager.hasHOG(name) is False:
            return None

        hog = HOGManager.getHOG(name)

        return hog.objectHOG
        pass

    @staticmethod
    def addHOG(name, hog):
        HOGManager.s_hogs[name] = hog
        pass

    pass
