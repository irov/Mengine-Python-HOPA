from Foundation.Object.DemonObject import DemonObject

class ObjectGuide(DemonObject):
    @staticmethod
    def declareORM(Type):
        DemonObject.declareORM(Type)
        Type.addParam(Type, 'PreviousSceneName')

    def _onParams(self, params):
        super(ObjectGuide, self)._onParams(params)
        self.initParam('PreviousSceneName', params, None)