from Foundation.Object.DemonObject import DemonObject

class ObjectMap(DemonObject):
    @staticmethod
    def declareORM(Type):
        DemonObject.declareORM(Type)

        Type.addParam(Type, "VisitScenes")
        Type.addParam(Type, "MarkedDone")
        Type.addParam(Type, "Teleport")
        Type.addParam(Type, "OpenPages")
        Type.addParam(Type, "CurrentID")
        pass

    def _onParams(self, params):
        super(ObjectMap, self)._onParams(params)
        self.initParam("VisitScenes", params, [])
        self.initParam("MarkedDone", params, [])
        self.initParam("Teleport", params, True)
        self.initParam("OpenPages", params, {})
        self.initParam("CurrentID", params, None)
        pass

    def removeAllData(self):
        self.setParam("VisitScenes", [])
        self.setParam("MarkedDone", [])
        self.setParam("OpenPages", {})
        self.setParam("CurrentID", None)
        pass
    pass