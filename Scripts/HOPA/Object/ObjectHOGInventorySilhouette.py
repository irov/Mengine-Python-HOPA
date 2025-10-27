from Foundation.Object.DemonObject import DemonObject


class ObjectHOGInventorySilhouette(DemonObject):
    @staticmethod
    def declareORM(Type):
        DemonObject.declareORM(Type)

        Type.declareParam("HOG")

        Type.declareParam("SlotCount")
        Type.declareParam("FindItems")
        Type.declareParam("FoundItems")

        pass

    def _onParams(self, params):
        super(ObjectHOGInventorySilhouette, self)._onParams(params)

        self.initParam("HOG", params, None)

        self.initParam("SlotCount", params, 0)
        self.initParam("FindItems", params, [])
        self.initParam("FoundItems", params, [])

        pass

    pass
