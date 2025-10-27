from HOPA.Object.ObjectEnigma import ObjectEnigma


class ObjectShootingRange(ObjectEnigma):
    @staticmethod
    def declareORM(Type):
        ObjectEnigma.declareORM(Type)

        Type.declareParam("Atitude")
        Type.declareParam("GunPos")
        pass

    def _onParams(self, params):
        super(ObjectShootingRange, self)._onParams(params)
        self.initParam("Atitude", params, None)
        self.initParam("GunPos", params, None)
        pass
