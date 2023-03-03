from Foundation.Object.Object import Object


class ObjectDifficulty2(Object):
    @staticmethod
    def declareORM(Type):
        Object.declareORM(Type)

    def _onParams(self, params):
        super(ObjectDifficulty2, self)._onParams(params)
