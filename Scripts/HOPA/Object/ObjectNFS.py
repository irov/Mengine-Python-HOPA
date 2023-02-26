from HOPA.Object.ObjectEnigma import ObjectEnigma

class ObjectNFS(ObjectEnigma):
    @staticmethod
    def declareORM(Type):
        ObjectEnigma.declareORM(Type)

        Type.addParam(Type, "ProgressBar")
        pass

    def _onParams(self, params):
        super(ObjectNFS, self)._onParams(params)
        self.initParam("ProgressBar", params, [(0.0, 0.0), (0.0, 0.0)])
        pass
    pass