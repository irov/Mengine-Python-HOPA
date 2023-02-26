from Foundation.Object.DemonObject import DemonObject

class ObjectReagents(DemonObject):
    @staticmethod
    def declareORM(Type):
        DemonObject.declareORM(Type)

        Type.addParam(Type, "OpenReagents")
        pass

    def _onParams(self, params):
        super(ObjectReagents, self)._onParams(params)

        self.initParam("OpenReagents", params, [])
        pass
    pass