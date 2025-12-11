from Foundation.Object.DemonObject import DemonObject


class ObjectCollectibles(DemonObject):
    @staticmethod
    def declareORM(Type):
        DemonObject.declareORM(Type)
        Type.declareParam('PreviousSceneName')
        Type.declareParam('CompleteScene')  # True if user collect all collectibles
        Type.declareParam('FinishAnimation')  # True if finish animation has been playing

        Type.declareParam('TransitionBackFromSceneName')
        Type.declareParam('TransitionBackToSceneName')
        Type.declareParam('TransitionBackToTextId')

    def _onParams(self, params):
        super(ObjectCollectibles, self)._onParams(params)
        self.initParam('PreviousSceneName', params, None)
        self.initParam('CompleteScene', params, False)
        self.initParam('FinishAnimation', params, False)

        self.initParam('TransitionBackFromSceneName', params, None)
        self.initParam('TransitionBackToSceneName', params, None)
        self.initParam('TransitionBackToTextId', params, None)
