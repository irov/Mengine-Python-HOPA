from Foundation.Object.DemonObject import DemonObject


class ObjectSkipPuzzle(DemonObject):
    @staticmethod
    def declareORM(Type):
        DemonObject.declareORM(Type)

        Type.declareParam("ForceReload")
        pass

    def _onParams(self, params):
        super(ObjectSkipPuzzle, self)._onParams(params)

        self.initParam("ForceReload", params, None)
        pass
