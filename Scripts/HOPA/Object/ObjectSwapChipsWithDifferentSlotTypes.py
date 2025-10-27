from HOPA.Object.ObjectEnigma import ObjectEnigma


class ObjectSwapChipsWithDifferentSlotTypes(ObjectEnigma):
    @staticmethod
    def declareORM(Type):
        ObjectEnigma.declareORM(Type)
        Type.declareParam('savedSlotChips')

    def _onParams(self, params):
        super(ObjectSwapChipsWithDifferentSlotTypes, self)._onParams(params)
        self.initParam('savedSlotChips', params, {})
