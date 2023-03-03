from Foundation.Object.DemonObject import DemonObject


class ObjectObjective(DemonObject):
    @staticmethod
    def declareORM(Type):
        DemonObject.declareORM(Type)

        Type.addParam(Type, "ObjectiveID")
        pass

    def _onParams(self, params):
        super(ObjectObjective, self)._onParams(params)

        self.initParam("ObjectiveID", params, None)
        pass

    pass
