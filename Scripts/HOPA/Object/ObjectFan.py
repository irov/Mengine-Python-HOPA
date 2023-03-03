from HOPA.Object.ObjectEnigma import ObjectEnigma


class ObjectFan(ObjectEnigma):
    PARAMS_Interactive = 0

    @staticmethod
    def declareORM(Type):
        ObjectEnigma.declareORM(Type)

        Type.addParam(Type, "FoundItems")
        Type.addParam(Type, "FindItems")
        Type.addParam(Type, "Polygon")
        Type.addParam(Type, "Open")
        Type.addParam(Type, "Hint")
        Type.addParam(Type, "HoldOpen")
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
