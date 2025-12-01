from Foundation.Object.DemonObject import DemonObject

class ObjectCutScene(DemonObject):
    @staticmethod
    def declareORM(Type):
        DemonObject.declareORM(Type)

        Type.declareParam("CutSceneName")
        Type.declareParam("Play")
        Type.declareParam("isFade")
        pass

    def _onParams(self, params):
        super(ObjectCutScene, self)._onParams(params)

        self.initParam("CutSceneName", params, None)
        self.initParam("Play", params, False)
        self.initParam("isFade", params, True)
        pass
