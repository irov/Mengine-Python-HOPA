from Foundation.Object.DemonObject import DemonObject


class ObjectTutorial(DemonObject):
    @staticmethod
    def declareORM(Type):
        DemonObject.declareORM(Type)

        Type.declareParam("Polygon")
        pass

    def _onParams(self, params):
        super(ObjectTutorial, self)._onParams(params)
        self.initParam("Polygon", params)
        pass
