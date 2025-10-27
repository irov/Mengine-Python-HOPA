from HOPA.Object.ObjectEnigma import ObjectEnigma


class ObjectHOG(ObjectEnigma):
    @staticmethod
    def declareORM(Type):
        ObjectEnigma.declareORM(Type)

        Type.declareParam("FoundItems")
        pass

    def _onParams(self, params):
        super(ObjectHOG, self)._onParams(params)

        self.initParam("FoundItems", params, [])
        pass

    pass
