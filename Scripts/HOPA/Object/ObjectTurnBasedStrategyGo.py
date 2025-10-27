from HOPA.Object.ObjectEnigma import ObjectEnigma


class ObjectTurnBasedStrategyGo(ObjectEnigma):
    @staticmethod
    def declareORM(Type):
        ObjectEnigma.declareORM(Type)
        Type.declareParam("NotCompleteLevels")
        Type.declareParam("CurrentLevel")

    def _onParams(self, params):
        super(ObjectTurnBasedStrategyGo, self)._onParams(params)
        self.initParam("NotCompleteLevels", params, [])
        self.initParam("CurrentLevel", params, None)
