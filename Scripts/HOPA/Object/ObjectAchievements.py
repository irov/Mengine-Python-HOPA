from Foundation.Object.DemonObject import DemonObject


class ObjectAchievements(DemonObject):
    @staticmethod
    def declareORM(Type):
        DemonObject.declareORM(Type)
        Type.addParam(Type, 'PreviousSceneName')

    def _onParams(self, params):
        super(ObjectAchievements, self)._onParams(params)
        self.initParam('PreviousSceneName', params, None)
