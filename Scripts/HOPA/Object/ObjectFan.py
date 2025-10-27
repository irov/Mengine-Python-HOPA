from HOPA.Object.ObjectEnigma import ObjectEnigma


class ObjectFan(ObjectEnigma):
    PARAMS_Interactive = 0

    @staticmethod
    def declareORM(Type):
        ObjectEnigma.declareORM(Type)

        Type.declareParam("FoundItems")
        Type.declareParam("FindItems")
        Type.declareParam("Polygon")
        Type.declareParam("Open")
        Type.declareParam("Hint")
        Type.declareParam("HoldOpen")
        pass

    def _onParams(self, params):
        super(ObjectFan, self)._onParams(params)

        self.initParam("FoundItems", params, [])
        self.initParam("FindItems", params, [])

        self.initParam("Polygon", params)
        self.initParam("Open", params, False)
        self.initParam("Hint", params, False)
        self.initParam("HoldOpen", params, False)
        pass

    pass
