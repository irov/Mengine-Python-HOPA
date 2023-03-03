from HOPA.Object.ObjectEnigma import ObjectEnigma


class ObjectSwapChipsInPlace(ObjectEnigma):
    @staticmethod
    def declareORM(Type):
        ObjectEnigma.declareORM(Type)
        Type.addParam(Type, 'completeEnigma')

    def _onParams(self, params):
        super(ObjectSwapChipsInPlace, self)._onParams(params)
        self.initParam('completeEnigma', params, False)
