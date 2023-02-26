from Foundation.DatabaseManager import DatabaseManager

class ExtrasManager(object):
    s_extras = {}

    class Extra(object):
        def __init__(self, buttonName, groupName, objectName, entityType, entityData):
            self.buttonName = buttonName
            self.groupName = groupName
            self.entityData = entityData
            self.entityType = entityType
            self.objectName = objectName
            pass

        def getButtonName(self):
            return self.buttonName
            pass

        def getGroupName(self):
            return self.groupName
            pass

        def getData(self):
            return self.entityData
            pass

        def getEntityType(self):
            return self.entityType
            pass

        def getObjectName(self):
            return self.objectName
            pass
        pass

    class ExtrasEnigma(object):
        def __init__(self, movieName, enigmaName, scenarioID):
            self.movieName = movieName
            self.enigmaName = enigmaName
            self.scenarioID = scenarioID
            pass

        def getMovieName(self):
            return self.movieName
            pass

        def getEnigmaName(self):
            return self.enigmaName
            pass

        def getScenarioID(self):
            return self.scenarioID
            pass
        pass

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            name = record.get("Name")

            buttonName = record.get("ButtonName")
            groupName = record.get("GroupName")
            objectName = record.get("ObjectName")
            entityType = record.get("Type")
            entityParam = record.get("Param")

            if entityType == "Enigma":
                entityData = ExtrasManager.loadExtrasEnigma(entityParam)
                pass
            else:
                entityData = None
                pass

            extra = ExtrasManager.Extra(buttonName, groupName, objectName, entityType, entityData)
            ExtrasManager.s_extras[name] = extra
            pass
        pass

    @staticmethod
    def loadExtrasEnigma(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        data = []
        for record in records:
            movieName = record.get("MovieName")
            enigmaName = record.get("EnigmaName")
            scenarioID = record.get("ScenarioID")

            dataElement = ExtrasManager.ExtrasEnigma(movieName, enigmaName, scenarioID)
            data.append(dataElement)
            pass
        return data
        pass

    @staticmethod
    def hasExtra(extraName):
        if extraName not in ExtrasManager.s_extras:
            return False
            pass

        return True
        pass

    @staticmethod
    def getExtra(extraName):
        return ExtrasManager.s_extras[extraName]
        pass
    pass

    @staticmethod
    def getExtras():
        if len(ExtrasManager.s_extras) == 0:
            Trace.log("Manager", 0, "ExtrasManager.getExtras: s_extras is empty")
            return None
            pass

        return ExtrasManager.s_extras
        pass
    pass

    @staticmethod
    def onFinalize():
        ExtrasManager.s_extras = {}
        pass