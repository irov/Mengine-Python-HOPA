from HOPA.Object.ObjectInventoryItem import ObjectInventoryItem

class ObjectInventoryCountItemFX(ObjectInventoryItem):
    @staticmethod
    def declareORM(Type):
        ObjectInventoryItem.declareORM(Type)

        Type.addParam(Type, "FontName")

        Type.addResource(Type, "ResourceMovieParts")
        Type.addResource(Type, "ResourceMovieCombine")
        Type.addResource(Type, "ResourceMovieFull")

        Type.addParam(Type, "ItemMovies")

        Type.addParam(Type, "PlayedItems")
        Type.addParam(Type, "Combined")

    def _onParams(self, params):
        super(ObjectInventoryCountItemFX, self)._onParams(params)

        self.initParam("FontName", params, None)

        self.initResource("ResourceMovieParts", params, None)
        self.initResource("ResourceMovieCombine", params, None)
        self.initResource("ResourceMovieFull", params, None)

        self.initParam("ItemMovies", params, [])

        self.initParam("PlayedItems", params, [])
        self.initParam("Combined", params, False)

    def _onInitialize(self):
        super(ObjectInventoryCountItemFX, self)._onInitialize()

        if _DEVELOPMENT is True:
            FontName = self.getFontName()
            if FontName is not None:
                if Mengine.hasFont(FontName) is False:
                    self.initializeFailed("Font %s not found" % (FontName))

    def hasItem(self, ItemName):
        FoundItems = self.getParam("FoundItems")

        if ItemName not in FoundItems:
            return False

        return True

    def takeItem(self, ItemName):
        FoundItems = self.getParam("FoundItems")

        if ItemName not in FoundItems:
            return True

        self.delParam("FoundItems", ItemName)

        if len(FoundItems) != 0:
            return True

        return False