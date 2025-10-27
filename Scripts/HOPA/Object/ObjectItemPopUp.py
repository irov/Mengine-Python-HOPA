from Foundation.Object.DemonObject import DemonObject


class ObjectItemPopUp(DemonObject):
    @staticmethod
    def declareORM(Type):
        DemonObject.declareORM(Type)

        Type.declareParam("ItemName")
        Type.declareParam("Open")
        pass

    def _onParams(self, params):
        super(ObjectItemPopUp, self)._onParams(params)

        self.initParam("ItemName", params, None)
        self.initParam("Open", params, False)
        pass

    pass
