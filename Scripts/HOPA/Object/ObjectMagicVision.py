from Foundation.Object.DemonObject import DemonObject

class ObjectMagicVision(DemonObject):
    @staticmethod
    def declareORM(Type):
        DemonObject.declareORM(Type)

        Type.addParam(Type, "State")
        Type.addParam(Type, "AllDoneScenes")
        Type.addParam(Type, "BlockedScenes")
        pass

    def _onParams(self, params):
        super(ObjectMagicVision, self)._onParams(params)
        self.initParam("State", params, "charging")
        self.initParam("AllDoneScenes", params, [])
        self.initParam("BlockedScenes", params, [])
        pass

    pass