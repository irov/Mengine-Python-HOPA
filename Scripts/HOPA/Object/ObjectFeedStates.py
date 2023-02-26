from HOPA.Object.ObjectEnigma import ObjectEnigma

class ObjectFeedStates(ObjectEnigma):
    @staticmethod
    def declareORM(Type):
        ObjectEnigma.declareORM(Type)

        Type.addParam(Type, "Saves")
        pass

    def _onParams(self, params):
        super(ObjectFeedStates, self)._onParams(params)
        self.initParam("Saves", params, {})
        pass