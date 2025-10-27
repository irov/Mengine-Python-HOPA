from Foundation.Object.DemonObject import DemonObject


class ObjectTip(DemonObject):
    @staticmethod
    def declareORM(Type):
        DemonObject.declareORM(Type)

        Type.declareParam("FixedPoint")
        Type.declareParam("PlayPolicy")
        pass

    def _onParams(self, params):
        super(ObjectTip, self)._onParams(params)

        self.initParam("FixedPoint", params, None)
        self.initParam("PlayPolicy", params, None)
        pass

    pass
