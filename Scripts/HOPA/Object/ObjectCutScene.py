from Foundation.Object.DemonObject import DemonObject


class ObjectCutScene(DemonObject):
    @staticmethod
    def declareORM(Type):
        DemonObject.declareORM(Type)

        Type.addParam(Type, "CutSceneName")
        Type.addParam(Type, "Play")
        pass

    def _onParams(self, params):
        super(ObjectCutScene, self)._onParams(params)
        self.initParam("CutSceneName", params, None)
        self.initParam("Play", params, False)
        self.initParam("isFade", params, True)
        pass

    pass
