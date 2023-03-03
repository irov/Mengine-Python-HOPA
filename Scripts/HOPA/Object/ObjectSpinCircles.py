from HOPA.Object.ObjectEnigma import ObjectEnigma


class ObjectSpinCircles(ObjectEnigma):
    @staticmethod
    def declareORM(Type):
        ObjectEnigma.declareORM(Type)

        Type.addParam(Type, "TwistSaves")
        Type.addParam(Type, "IndicatorSaves")
        Type.addParam(Type, "MovieLoop")
        Type.addParam(Type, "Related")
        pass

    def _onParams(self, params):
        super(ObjectSpinCircles, self)._onParams(params)
        self.initParam("TwistSaves", params, {})
        self.initParam("IndicatorSaves", params, {})
        self.initParam("MovieLoop", params, True)
        self.initParam("Related", params, False)
        pass

    pass
