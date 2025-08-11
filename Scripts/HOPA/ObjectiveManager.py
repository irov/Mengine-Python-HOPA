from Foundation.Manager import Manager

from Foundation.DatabaseManager import DatabaseManager

class ObjectiveManager(object):
    s_objectives = {}

    class Object(object):
        def __init__(self, textID):
            self.textID = textID

    @staticmethod
    def _onFinalize():
        ObjectiveManager.s_objectives = {}
        pass

    @staticmethod
    def loadObjectives(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)
        for record in records:
            ID_OBJECTIVE = record.get("ID_OBJECTIVE")
            ID_TEXT = record.get("ID_TEXT")

            ObjectiveManager.addObjective(ID_OBJECTIVE, ID_TEXT)

    @staticmethod
    def hasObjective(objectiveID):
        return objectiveID in ObjectiveManager.s_objectives

    @staticmethod
    def addObjective(objectiveID, textID):
        objective = ObjectiveManager.Object(textID)
        ObjectiveManager.s_objectives[objectiveID] = objective

    @staticmethod
    def getObjective(objectiveID):
        if ObjectiveManager.hasObjective(objectiveID) is False:
            Trace.log("Manager", 0, "ObjectiveManager.getObjective: not found objective id %s" % (objectiveID))
            pass

        objective = ObjectiveManager.s_objectives[objectiveID]
        return objective

    @staticmethod
    def getObjectiveTextID(objectiveID):
        objective = ObjectiveManager.getObjective(objectiveID)
        return objective.textID
