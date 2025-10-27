from Foundation.Object.DemonObject import DemonObject


class ObjectMap2(DemonObject):
    @staticmethod
    def declareORM(Type):
        DemonObject.declareORM(Type)

        Type.declareParam("OpenScenes")
        Type.declareParam("BlockedScenes")
        Type.declareParam("OpenHog")
        Type.declareParam("PlayedOpenHog")
        Type.declareParam('CompletedScenes')

    def _onParams(self, params):
        super(ObjectMap2, self)._onParams(params)
        self.initParam("OpenScenes", params, [])
        self.initParam("BlockedScenes", params, [])
        self.initParam("OpenHog", params, [])
        self.initParam("PlayedOpenHog", params, [])
        self.initParam("CompletedScenes", params, [])
