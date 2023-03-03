from HOPA.Object.ObjectEnigma import ObjectEnigma


class ObjectHOG2(ObjectEnigma):
    @staticmethod
    def declareORM(Type):
        ObjectEnigma.declareORM(Type)

        Type.addParam(Type, "FoundItems")

        Type.addParam(Type, "PrepareItems")

        pass

    def _onParams(self, params):
        super(ObjectHOG2, self)._onParams(params)

        self.initParam("FoundItems", params, [])

        self.initParam("PrepareItems", params, [])
        pass

    pass
