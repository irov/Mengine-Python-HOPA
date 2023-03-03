from Foundation.Object.DemonObject import DemonObject
from HOPA.HOGFittingItemManager import HOGFittingItemManager


class ObjectHOGInventoryFitting(DemonObject):
    @staticmethod
    def declareORM(Type):
        DemonObject.declareORM(Type)

        Type.addParam(Type, "SlotCount")
        Type.addParam(Type, "SlotItems")
        Type.addParam(Type, "SlotIsFitting")
        Type.addParam(Type, "ItemList")
        Type.addParam(Type, "SlotFittingItemList")
        Type.addParam(Type, "SlotFittingItemListUsed")

    def _onParams(self, params):
        super(ObjectHOGInventoryFitting, self)._onParams(params)
        self.initParam("SlotCount", params, 0)
        self.initParam("SlotItems", params, [])
        self.initParam("SlotIsFitting", params, [])
        self.initParam("ItemList", params, [])
        self.initParam("SlotFittingItemList", params, [])
        self.initParam("SlotFittingItemListUsed", params, [])

    def getInventoryItem(self, itemName):
        InventoryItem = HOGFittingItemManager.getItemObject(itemName, self)

        return InventoryItem

    def getInventoryItemKey(self, invItem):
        ItemKey = HOGFittingItemManager.getInventoryItemKey(invItem)
        return ItemKey

    def getItemTextID(self, itemName):
        textID = HOGFittingItemManager.getTextID(itemName)
        return textID

    def attachItemSlotMovie(self, ItemKey, tempMovie):
        movieEntityNode = tempMovie.getEntityNode()
        invEntity = self.getEntity()

        itemSlot = invEntity.getSlotByName(ItemKey)
        itemSlot.MovieSlot.addChild(movieEntityNode)
        if itemSlot.SlotIsFitting is False:
            item = itemSlot.ItemStore
        else:
            item = itemSlot.ItemHideStore

        item.setPosition((0, 0))

        # movieEntity = tempMovie.getEntity()
        # movieNode = movieEntity.getAnimatable()
        # movieSize = movieNode.getSize()

        pos = itemSlot.getItemOffset(item)

        # MovieOffset = (pos[0]-(movieSize.x * 0.5), pos[1]-(movieSize.y * 0.5))
        MovieOffset = pos
        movieEntityNode = tempMovie.getEntityNode()
        movieEntityNode.setLocalPosition(MovieOffset)

    def returnItemSlot(self, ItemKey):
        invEntity = self.getEntity()
        slot = invEntity.getSlotByName(ItemKey)
        if slot is None:
            return
        if slot.pick is True:
            return

        slot.ReturnItem()

    def hasFreeSlot(self):
        invEntity = self.getEntity()
        return invEntity.hasFreeSlot()
