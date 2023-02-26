from Foundation.Object.DemonObject import DemonObject

class ObjectMind(DemonObject):
    @staticmethod
    def declareORM(Type):
        DemonObject.declareORM(Type)

        Type.addParam(Type, "DetectPoint")
        pass

    def _onParams(self, params):
        super(ObjectMind, self)._onParams(params)
        self.initParam("PlayPolicy", params, None)
        pass
    pass