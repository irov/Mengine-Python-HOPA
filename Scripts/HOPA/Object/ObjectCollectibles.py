from Foundation.Object.DemonObject import DemonObject

class ObjectCollectibles(DemonObject):
    @staticmethod
    def declareORM(Type):
        DemonObject.declareORM(Type)
        Type.addParam(Type, 'PreviousSceneName')
        Type.addParam(Type, 'CompleteScene')  # True if user collect all collectibles
        Type.addParam(Type, 'FinishAnimation')  # True if finish animation has been playing

    def _onParams(self, params):
        super(ObjectCollectibles, self)._onParams(params)
        self.initParam('PreviousSceneName', params, None)
        self.initParam('CompleteScene', params, False)
        self.initParam('FinishAnimation', params, False)