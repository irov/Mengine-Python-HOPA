from HOPA.Object.ObjectEnigma import ObjectEnigma


class ObjectPlanetGame(ObjectEnigma):
    @staticmethod
    def declareORM(Type):
        ObjectEnigma.declareORM(Type)

        Type.declareParam("Planets")
        pass

    def _onParams(self, params):
        super(ObjectPlanetGame, self)._onParams(params)

        self.initParam("Planets", params, {})
        pass
