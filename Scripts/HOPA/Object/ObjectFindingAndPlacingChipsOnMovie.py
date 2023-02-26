from HOPA.Object.ObjectEnigma import ObjectEnigma

class ObjectFindingAndPlacingChipsOnMovie(ObjectEnigma):
    @staticmethod
    def declareORM(Type):
        ObjectEnigma.declareORM(Type)
        Type.addParam(Type, "RemainingChips")

    def _onParams(self, params):
        super(ObjectFindingAndPlacingChipsOnMovie, self)._onParams(params)
        self.initParam("RemainingChips", params, [])