from Foundation.Object.DemonObject import DemonObject

class ObjectMahjongInventory(DemonObject):
    @staticmethod
    def declareORM(Type):
        DemonObject.declareORM(Type)

        Type.addParam(Type, "TextID")
        Type.addParam(Type, "EnigmaName")

        Type.addParam(Type, "ItemsCount")
        Type.addParam(Type, "FoundItems")

    def _onParams(self, params):
        super(ObjectMahjongInventory, self)._onParams(params)
        self.initParam("TextID", params, None)
        self.initParam("EnigmaName", params, None)

        self.initParam("ItemsCount", params, None)
        self.initParam("FoundItems", params, [])