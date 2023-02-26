from HOPA.Object.ObjectEnigma import ObjectEnigma

class ObjectClickOnChipsInTheRightOrder(ObjectEnigma):
    @staticmethod
    def declareORM(Type):
        ObjectEnigma.declareORM(Type)
        Type.addParam(Type, 'finishFlag')

    def _onParams(self, params):
        super(ObjectClickOnChipsInTheRightOrder, self)._onParams(params)
        self.initParam('finishFlag', params, False)