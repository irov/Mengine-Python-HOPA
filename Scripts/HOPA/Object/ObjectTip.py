from Foundation.Object.DemonObject import DemonObject


class ObjectTip(DemonObject):
    @staticmethod
    def declareORM(Type):
        DemonObject.declareORM(Type)

        Type.addParam(Type, "FixedPoint")
        Type.addParam(Type, "PlayPolicy")
        pass

    def _onParams(self, params):
        super(ObjectTip, self)._onParams(params)

        self.initParam("FixedPoint", params, None)
        self.initParam("PlayPolicy", params, None)
        pass

    pass
