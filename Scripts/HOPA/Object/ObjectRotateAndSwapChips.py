from HOPA.Object.ObjectEnigma import ObjectEnigma

class ObjectRotateAndSwapChips(ObjectEnigma):
    def _onParams(self, params):
        super(ObjectRotateAndSwapChips, self)._onParams(params)
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