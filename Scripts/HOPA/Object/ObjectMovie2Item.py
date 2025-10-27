from Foundation.Object.DemonObject import DemonObject


class ObjectMovie2Item(DemonObject):
    @staticmethod
    def declareORM(Type):
        DemonObject.declareORM(Type)
        Type.declareConst("CompositionNameIdle")
        Type.declareConst("CompositionNamePick")

        Type.declareConst("ResourceMovie")
        pass

    def _onParams(self, params):
        super(ObjectMovie2Item, self)._onParams(params)
        self.initConst("CompositionNameIdle", params)
        self.initConst("CompositionNamePick", params, None)

        self.initConst("ResourceMovie", params)
        pass

    pass
