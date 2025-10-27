from HOPA.Object.ObjectEnigma import ObjectEnigma


class ObjectHOGSilhouette(ObjectEnigma):
    @staticmethod
    def declareORM(Type):
        ObjectEnigma.declareORM(Type)

        Type.declareParam("FoundItems")
        Type.declareParam("FindItems")
        pass

    def _onParams(self, params):
        super(ObjectHOGSilhouette, self)._onParams(params)

        self.initParam("FoundItems", params, [])
        self.initParam("FindItems", params, [])
        pass

    pass
