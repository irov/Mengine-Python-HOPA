from Foundation.Object.DemonObject import DemonObject


class ObjectMovie2Item(DemonObject):
    @staticmethod
    def declareORM(Type):
        DemonObject.declareORM(Type)
        Type.addConst(Type, "CompositionNameIdle")
        Type.addConst(Type, "CompositionNamePick")

        Type.addConst(Type, "ResourceMovie")
        pass

    def _onParams(self, params):
        super(ObjectMovie2Item, self)._onParams(params)
        self.initConst("CompositionNameIdle", params)
        self.initConst("CompositionNamePick", params, None)

        self.initConst("ResourceMovie", params)
        pass

    pass
