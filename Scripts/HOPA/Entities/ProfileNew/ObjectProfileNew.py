from Foundation.Object.Object import Object


class ObjectProfileNew(Object):
    @staticmethod
    def declareORM(Type):
        Object.declareORM(Type)

        Type.declareParam("AccountID")
        Type.declareParam("ClickSlotID")
        pass

    def _onParams(self, params):
        super(ObjectProfileNew, self)._onParams(params)

        self.initParam("AccountID", params, None)
        self.initParam("ClickSlotID", params, None)
        pass
