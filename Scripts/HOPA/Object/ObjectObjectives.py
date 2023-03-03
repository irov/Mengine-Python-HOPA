from Foundation.Object.DemonObject import DemonObject


class ObjectObjectives(DemonObject):
    @staticmethod
    def declareORM(Type):
        DemonObject.declareORM(Type)

        Type.addParam(Type, "ObjectivesList")
        pass

    def _onParams(self, params):
        super(ObjectObjectives, self)._onParams(params)
        self.initParam("ObjectivesList", params, [])
        pass

    pass
