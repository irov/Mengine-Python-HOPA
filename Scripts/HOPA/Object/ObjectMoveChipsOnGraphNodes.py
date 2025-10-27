from HOPA.Object.ObjectEnigma import ObjectEnigma


class ObjectMoveChipsOnGraphNodes(ObjectEnigma):
    @staticmethod
    def declareORM(Type):
        ObjectEnigma.declareORM(Type)
        Type.declareParam('savedSlotChips')

    def _onParams(self, params):
        super(ObjectMoveChipsOnGraphNodes, self)._onParams(params)
        self.initParam('savedSlotChips', params, {})
