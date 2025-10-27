from HOPA.Object.ObjectEnigma import ObjectEnigma


class ObjectColoringPuzzle(ObjectEnigma):

    @staticmethod
    def declareORM(Type):
        ObjectEnigma.declareORM(Type)

        Type.declareParam("Mix")
        pass

    def _onParams(self, params):
        super(ObjectColoringPuzzle, self)._onParams(params)
        self.initParam("Mix", params, {})
        pass

    def play(self):
        self.setParam("Play", True)
        self.setEnable(True)
        pass

    def isSavable(self):
        return True
        pass

    def _onSave(self):
        return None
        pass

    def _onLoad(self, load_obj):
        pass

    pass
