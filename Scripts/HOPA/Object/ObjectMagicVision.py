from Foundation.Object.DemonObject import DemonObject


class ObjectMagicVision(DemonObject):
    @staticmethod
    def declareORM(Type):
        DemonObject.declareORM(Type)

        Type.declareParam("State")
        Type.declareParam("AllDoneScenes")
        Type.declareParam("BlockedScenes")
        pass

    def _onParams(self, params):
        super(ObjectMagicVision, self)._onParams(params)
        self.initParam("State", params, "charging")
        self.initParam("AllDoneScenes", params, [])
        self.initParam("BlockedScenes", params, [])
        pass

    pass
