from Foundation.Object.DemonObject import DemonObject


class ObjectTipItem(DemonObject):
    @staticmethod
    def declareORM(Type):
        DemonObject.declareORM(Type)

        Type.addParam(Type, "TipItemID")
        pass

    def _onParams(self, params):
        super(ObjectTipItem, self)._onParams(params)

        self.initParam("TipItemID", params, None)
        pass

    pass
