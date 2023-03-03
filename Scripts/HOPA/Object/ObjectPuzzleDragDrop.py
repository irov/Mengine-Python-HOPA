from HOPA.Object.ObjectEnigma import ObjectEnigma


class ObjectPuzzleDragDrop(ObjectEnigma):
    @staticmethod
    def declareORM(Type):
        ObjectEnigma.declareORM(Type)

        Type.addParam(Type, "Items")
        Type.addParam(Type, "Places")
        Type.addParam(Type, "HoldItems")
        Type.addParam(Type, "DisableItems")
        pass

    def _onParams(self, params):
        super(ObjectPuzzleDragDrop, self)._onParams(params)

        self.initParam("Items", params, [])
        self.initParam("Places", params, {})
        self.initParam("HoldItems", params, [])
        self.initParam("DisableItems", params, [])
        pass

    pass
