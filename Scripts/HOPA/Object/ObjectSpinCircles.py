from HOPA.Object.ObjectEnigma import ObjectEnigma


class ObjectSpinCircles(ObjectEnigma):
    @staticmethod
    def declareORM(Type):
        ObjectEnigma.declareORM(Type)

        Type.declareParam("TwistSaves")
        Type.declareParam("IndicatorSaves")
        Type.declareParam("MovieLoop")
        Type.declareParam("Related")
        pass

    def _onParams(self, params):
        super(ObjectSpinCircles, self)._onParams(params)
        self.initParam("TwistSaves", params, {})
        self.initParam("IndicatorSaves", params, {})
        self.initParam("MovieLoop", params, True)
        self.initParam("Related", params, False)
        pass

    pass
