from Foundation.Object.DemonObject import DemonObject


class ObjectHOGInventoryCount(DemonObject):
    @staticmethod
    def declareORM(Type):
        DemonObject.declareORM(Type)
        Type.declareParam("HOG")

        Type.declareParam("TextID")
        Type.declareParam("EnigmaName")

        Type.declareParam("FindItems")
        Type.declareParam("FoundItems")
        Type.declareParam("ItemsCount")

    def _onParams(self, params):
        super(ObjectHOGInventoryCount, self)._onParams(params)
        self.initParam("HOG", params, None)

        self.initParam("TextID", params, None)
        self.initParam("EnigmaName", params, None)

        self.initParam("FindItems", params, [])
        self.initParam("FoundItems", params, [])
        self.initParam("ItemsCount", params, None)
