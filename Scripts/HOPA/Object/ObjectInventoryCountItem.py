from Foundation.Object.Object import Object
from HOPA.ItemManager import ItemManager
from HOPA.PopUpItemManager import PopUpItemManager

class ObjectInventoryCountItem(Object):

    @staticmethod
    def declareORM(Type):
        Object.declareORM(Type)

        Type.addResource(Type, "SpriteResourceName")
        Type.addParam(Type, "FontName")
        Type.addParam(Type, "SlotPoint")
        Type.addParam(Type, "ArrowPoint")
        Type.addParam(Type, "FoundItems")

    def _onParams(self, params):
        super(ObjectInventoryCountItem, self)._onParams(params)

        self.initResource("SpriteResourceName", params, None)
        self.initParam("FontName", params, None)
        self.initParam("SlotPoint", params, None)
        self.initParam("ArrowPoint", params, (0, 0))

        self.initParam("FoundItems", params, [])

    def _onInitialize(self):
        super(ObjectInventoryCountItem, self)._onInitialize()

        if _DEVELOPMENT is True:
            FontName = self.getFontName()
            if FontName is not None:
                if Mengine.hasFont(FontName) is False:
                    self.initializeFailed("Font %s not found" % (FontName))

    def _getProgressTotal(self):
        FindItems = ItemManager.getInventoryItemFindItems(self)
        if FindItems is None:
            # FindItems may be empty in case of CountItem using for ItemPopUp
            FindItems = PopUpItemManager.getInventoryItemFindItems(self)

        total = 0
        for find_item in FindItems:
            Item = ItemManager.getItem(find_item)

            count = Item.ItemPartsCount
            if count is None:
                total += 1
                continue

            total += count

        progress = 0
        for found_item in self.getParam("FoundItems"):
            Item = ItemManager.getItem(found_item)

            count = Item.ItemPartsCount
            if count is None:
                progress += 1
                continue

            progress += count

        return progress, total

    def checkCount(self):
        progress, total = self._getProgressTotal()

        if progress == total:
            return True
        return False

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