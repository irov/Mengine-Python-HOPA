from Foundation.Object.DemonObject import DemonObject


class ObjectHOGInventory(DemonObject):
    @staticmethod
    def declareORM(Type):
        DemonObject.declareORM(Type)

        Type.declareParam("HOGName")
        Type.declareParam("HOGItems")
        Type.declareParam("FoundItems")
        Type.declareParam("Wrap")
        Type.declareParam("MaxItemTextWrap")
        Type.declareParam("MaxColumn")
        Type.declareParam("MaxRow")
        pass

    def _onParams(self, params):
        super(ObjectHOGInventory, self)._onParams(params)

        self.initParam("HOGName", params, None)
        self.initParam("HOGItems", params, [])
        self.initParam("FoundItems", params, [])

        self.initParam("Wrap", params, [(0, 0), (0, 0)])
        self.initParam("MaxItemTextWrap", params, [])
        self.initParam("MaxColumn", params, 0)
        self.initParam("MaxRow", params, 0)
        pass

    pass
