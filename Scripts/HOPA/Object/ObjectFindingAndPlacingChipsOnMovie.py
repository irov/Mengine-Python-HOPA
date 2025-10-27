from HOPA.Object.ObjectEnigma import ObjectEnigma


class ObjectFindingAndPlacingChipsOnMovie(ObjectEnigma):
    @staticmethod
    def declareORM(Type):
        ObjectEnigma.declareORM(Type)
        Type.declareParam("RemainingChips")

    def _onParams(self, params):
        super(ObjectFindingAndPlacingChipsOnMovie, self)._onParams(params)
        self.initParam("RemainingChips", params, [])
