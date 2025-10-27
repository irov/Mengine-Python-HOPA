from Foundation.Object.DemonObject import DemonObject


class ObjectHOGInventoryImage(DemonObject):
    @staticmethod
    def declareORM(Type):
        DemonObject.declareORM(Type)

        Type.declareParam("HOG")
        Type.declareParam("FindItems")
        Type.declareParam("FoundItems")
        Type.declareParam("ItemsCount")
        Type.declareParam("SlotCount")
        Type.declareParam("Slots")
        pass

    def _onParams(self, params):
        super(ObjectHOGInventoryImage, self)._onParams(params)

        self.initParam("HOG", params, None)

        self.initParam("FindItems", params, [])
        self.initParam("FoundItems", params, [])
        self.initParam("ItemsCount", params, None)

        self.initParam("SlotCount", params)
        self.initParam("Slots", params, {})

        pass

    pass
