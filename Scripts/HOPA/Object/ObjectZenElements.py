from HOPA.Object.ObjectEnigma import ObjectEnigma


class ObjectZenElements(ObjectEnigma):
    @staticmethod
    def declareORM(Type):
        ObjectEnigma.declareORM(Type)

        Type.addParam(Type, "ItemParentMap")
        Type.addParam(Type, "Frames")
        pass

    def _onParams(self, params):
        super(ObjectZenElements, self)._onParams(params)
        self.initParam("ItemParentMap", params, {})
        self.initParam("Frames", params, {})
        pass

    pass
