from HOPA.Object.ObjectEnigma import ObjectEnigma


class ObjectCirclePairElements(ObjectEnigma):

    @staticmethod
    def declareORM(Type):
        ObjectEnigma.declareORM(Type)

        Type.declareParam("SaveNames")
        Type.declareParam("SaveCircles")
        pass

    def _onParams(self, params):
        super(ObjectCirclePairElements, self)._onParams(params)
        self.initParam("SaveNames", params, [])
        self.initParam("SaveCircles", params, [])
        pass

    pass
