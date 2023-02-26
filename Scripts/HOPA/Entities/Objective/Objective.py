from Foundation.Entity.BaseEntity import BaseEntity

from HOPA.ObjectiveManager import ObjectiveManager

class Objective(BaseEntity):

    @staticmethod
    def declareORM(Type):
        BaseEntity.declareORM(Type)

        Type.addAction(Type, "ObjectiveID", Update=Objective._updateObjectiveID)
        pass

    def __init__(self):
        super(Objective, self).__init__()

        self.objectiveID = None
        pass

    def _updateObjectiveID(self, objectiveID):
        self.objectiveID = objectiveID

        Text_Message = self.object.getObject("Text_Message")

        if self.objectiveID is not None:
            objective = ObjectiveManager.getObjective(self.objectiveID)

            Text_Message.setParams(Enable=True, TextID=objective.textID)
        else:
            Text_Message.setParams(Enable=False)
            pass
        pass
    pass