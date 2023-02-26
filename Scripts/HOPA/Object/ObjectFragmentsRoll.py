from HOPA.Object.ObjectEnigma import ObjectEnigma

class ObjectFragmentsRoll(ObjectEnigma):
    def _onParams(self, params):
        super(ObjectFragmentsRoll, self)._onParams(params)
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