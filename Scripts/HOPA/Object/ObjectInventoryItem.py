from Foundation.Object.Object import Object

class ObjectInventoryItem(Object):

    @staticmethod
    def declareORM(Type):
        Object.declareORM(Type)

        Type.addResource(Type, "SpriteResourceName")
        Type.addParam(Type, "SlotPoint")
        Type.addParam(Type, "ArrowPoint")
        Type.addParam(Type, "FoundItems")

    def _onParams(self, params):
        super(ObjectInventoryItem, self)._onParams(params)

        self.initResource("SpriteResourceName", params, None)

        self.initParam("SlotPoint", params, None)
        self.initParam("ArrowPoint", params, (0, 0))

        self.initParam("FoundItems", params, [])

    def checkCount(self):
        return True

    def hasItem(self, ItemName):
        return True

    def takeItem(self, ItemName):
        return True