from HOPA.Object.ObjectEnigma import ObjectEnigma

class ObjectMahjong(ObjectEnigma):
    @staticmethod
    def declareORM(Type):
        ObjectEnigma.declareORM(Type)
        Type.addParam(Type, "FoundPairs")

    def _onParams(self, params):
        super(ObjectMahjong, self)._onParams(params)
        self.initParam("FoundPairs", params, [])