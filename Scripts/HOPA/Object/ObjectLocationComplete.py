from Foundation.Object.DemonObject import DemonObject


class ObjectLocationComplete(DemonObject):
    @staticmethod
    def declareORM(Type):
        DemonObject.declareORM(Type)

        Type.declareParam("CompleteScenes")
        pass

    def _onParams(self, params):
        super(ObjectLocationComplete, self)._onParams(params)
        self.initParam("CompleteScenes", params, [])
        pass

    pass
