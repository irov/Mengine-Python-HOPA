from Foundation.Object.Object import Object

class ObjectMetalDetector(Object):
    @staticmethod
    def declareORM(Type):
        DemonObject.declareORM(Type)

        Type.addParam(Type, "DetectPoint")
        pass

    def _onParams(self, params):
        super(ObjectMetalDetector, self)._onParams(params)

        self.initParam("DetectPoint", params, (0, 0))
        pass