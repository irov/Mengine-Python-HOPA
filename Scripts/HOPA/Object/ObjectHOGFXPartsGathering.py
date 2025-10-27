from HOPA.Object.ObjectEnigma import ObjectEnigma


class ObjectHOGFXPartsGathering(ObjectEnigma):
    @staticmethod
    def declareORM(Type):
        ObjectEnigma.declareORM(Type)

        Type.declareParam("FoundItems")

    def _onParams(self, params):
        super(ObjectHOGFXPartsGathering, self)._onParams(params)

        self.initParam("FoundItems", params, [])
