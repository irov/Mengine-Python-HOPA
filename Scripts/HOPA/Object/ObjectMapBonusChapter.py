from Foundation.Object.DemonObject import DemonObject


class ObjectMapBonusChapter(DemonObject):
    @staticmethod
    def declareORM(Type):
        DemonObject.declareORM(Type)

        Type.addParam(Type, "OpenScenes")
        Type.addParam(Type, "BlockedScenes")
        Type.addParam(Type, "OpenHog")
        Type.addParam(Type, "PlayedOpenHog")
        Type.addParam(Type, 'CompletedScenes')

    def _onParams(self, params):
        super(ObjectMapBonusChapter, self)._onParams(params)
        self.initParam("OpenScenes", params, [])
        self.initParam("BlockedScenes", params, [])
        self.initParam("OpenHog", params, [])
        self.initParam("PlayedOpenHog", params, [])
        self.initParam("CompletedScenes", params, [])
