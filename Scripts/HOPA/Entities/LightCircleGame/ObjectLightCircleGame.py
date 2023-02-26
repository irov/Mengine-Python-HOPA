from HOPA.Object.ObjectEnigma import ObjectEnigma

class ObjectLightCircleGame(ObjectEnigma):
    def _onParams(self, params):
        super(ObjectLightCircleGame, self)._onParams(params)
        self.initParam("CirclesAngle", params, None)
        pass
    pass