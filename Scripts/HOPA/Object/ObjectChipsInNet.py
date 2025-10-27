from HOPA.Object.ObjectEnigma import ObjectEnigma


class ObjectChipsInNet(ObjectEnigma):
    @staticmethod
    def declareORM(Type):
        ObjectEnigma.declareORM(Type)
        Type.declareParam('finishFlag')

    def _onParams(self, params):
        super(ObjectChipsInNet, self)._onParams(params)
        self.initParam('finishFlag', params, False)
