from Foundation.Object.DemonObject import DemonObject
from Foundation.TaskManager import TaskManager
from Foundation.SystemManager import SystemManager

class ObjectAdvertisingScene(DemonObject):
    @staticmethod
    def declareORM(Type):
        DemonObject.declareORM(Type)
        Type.addParam(Type, "TransitionData")
        Type.addParam(Type, "Placement")

    def _onParams(self, params):
        super(ObjectAdvertisingScene, self)._onParams(params)
        self.initParam("TransitionData", params, None)
        self.initParam("Placement", params, False)