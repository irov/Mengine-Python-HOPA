from Foundation.Object.Object import Object


class ObjectPuzzleRules(Object):
    @staticmethod
    def declareORM(Type):
        Object.declareORM(Type)

        Type.addParam(Type, "PuzzleName")
        pass

    def _onParams(self, params):
        super(ObjectPuzzleRules, self)._onParams(params)
        self.initParam("PuzzleName", params, None)
        pass

    pass
