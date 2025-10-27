from Foundation.Object.DemonObject import DemonObject


class ObjectSpot(DemonObject):
    @staticmethod
    def declareORM(Type):
        DemonObject.declareORM(Type)

        Type.declareParam("FadeColor")
        pass

    def _onParams(self, params):
        super(ObjectSpot, self)._onParams(params)
        self.initParam("FadeColor", params, (1.0, 1.0, 1.0))
        pass

    pass
