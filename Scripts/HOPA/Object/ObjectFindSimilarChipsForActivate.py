from HOPA.Object.ObjectEnigma import ObjectEnigma


class ObjectFindSimilarChipsForActivate(ObjectEnigma):
    @staticmethod
    def declareORM(Type):
        ObjectEnigma.declareORM(Type)
        Type.declareParam('availablePlaces')

    def _onParams(self, params):
        super(ObjectFindSimilarChipsForActivate, self)._onParams(params)
        self.initParam('availablePlaces', params, {})
