from HOPA.Object.ObjectEnigma import ObjectEnigma


class ObjectTrafficJam(ObjectEnigma):
    @staticmethod
    def declareORM(Type):
        ObjectEnigma.declareORM(Type)

        Type.declareParam("PoleSize")
        Type.declareParam("CellWrap")
        Type.declareParam("CellPosition")
        Type.declareParam("Goal")
        pass

    def _onParams(self, params):
        super(ObjectTrafficJam, self)._onParams(params)

        self.initParam("PoleSize", params)
        self.initParam("CellWrap", params)
        self.initParam("CellPosition", params)
        self.initParam("Goal", params)
        pass

    def isSavable(self):
        return True
        pass

    def _onSave(self):
        return None
        pass

    def _onLoad(self, load_obj):
        return None
        pass

    pass
