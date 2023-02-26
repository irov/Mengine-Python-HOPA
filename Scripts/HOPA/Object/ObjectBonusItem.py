from Foundation.Object.Object import Object

class ObjectBonusItem(Object):
    @staticmethod
    def declareORM(Type):
        Object.declareORM(Type)

        Type.addParam(Type, "ItemsCount")
        pass

    def _onParams(self, params):
        super(ObjectBonusItem, self)._onParams(params)

        self.initParam("ItemsCount", params, 0)
        pass
    pass