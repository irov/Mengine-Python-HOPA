from HOPA.Object.ObjectEnigma import ObjectEnigma

class ObjectSameElements(ObjectEnigma):
    @staticmethod
    def declareORM(Type):
        ObjectEnigma.declareORM(Type)
        Type.addParam(Type, "Collections")
        pass

    def _onParams(self, params):
        super(ObjectSameElements, self)._onParams(params)
        self.initParam("Collections", params, {})
        pass
    pass