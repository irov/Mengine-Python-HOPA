from HOPA.Object.ObjectEnigma import ObjectEnigma

class ObjectHOGRolling(ObjectEnigma):
    @staticmethod
    def declareORM(Type):
        ObjectEnigma.declareORM(Type)

        Type.addParam(Type, "FoundItems")
        Type.addParam(Type, "FindItems")
        pass

    def _onParams(self, params):
        super(ObjectHOGRolling, self)._onParams(params)

        self.initParam("FoundItems", params, [])
        self.initParam("FindItems", params, [])
        pass

    pass