from HOPA.Object.ObjectEnigma import ObjectEnigma

class ObjectSpinCirclesMastermind(ObjectEnigma):
    def _onParams(self, params):
        super(ObjectSpinCirclesMastermind, self)._onParams(params)
        self.initParam("UpNum", params, None)
        self.initParam("DownNum", params, None)
        pass

    pass