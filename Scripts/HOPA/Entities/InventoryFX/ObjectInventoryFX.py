from Foundation.ArrowManager import ArrowManager
from Foundation.DefaultManager import DefaultManager
from Foundation.Object.DemonObject import DemonObject
from HOPA.ItemManager import ItemManager

class ObjectInventoryFX(DemonObject):
    @staticmethod
    def declareORM(Type):
        DemonObject.declareORM(Type)

        Type.declareParam("CurrentSlotIndex")
        Type.declareParam("InventoryItems")
        Type.declareParam("SlotCount")
        Type.declareParam("SlotPolygon")
        Type.declareParam("SlotPoints")

    def _onParams(self, params):
        super(ObjectInventoryFX, self)._onParams(params)
        self.initParam("CurrentSlotIndex", params, 0)
        self.initParam("InventoryItems", params, [])
        self.initParam("SlotCount", params, 0)
        self.initParam("SlotPolygon", params, None)
        self.initParam("SlotPoints", params, None)

    def addItem(self, itemName):
        InventoryItem = ItemManager.getItemInventoryItem(itemName)
        self.addInventoryItem(InventoryItem)

    def getInventoryItem(self, itemName):
        InventoryItem = ItemManager.getItemInventoryItem(itemName)
        return InventoryItem

    def getInventoryItemKey(self, invItem):
        ItemKey = ItemManager.getInventoryItemKey(invItem)
        return ItemKey

    def getItemTextID(self, itemName):
        textID = ItemManager.getTextID(itemName)
        return textID

    def attachItemSlotMovie(self, ItemKey, tempMovie):
        InvItem = ItemManager.getItemInventoryItem(ItemKey)
        movieEntity = tempMovie.getEntity()
        movieEntityNode = tempMovie.getEntityNode()
        invEntity = self.getEntity()
        itemSlot = invEntity.findSlot(InvItem)
        itemSlot.point.addChild(movieEntityNode)

        movieNode = movieEntity.getAnimatable()
        movieSize = movieNode.getSize()
        MovieOffset = (-(movieSize.x * 0.5), -(movieSize.y * 0.5))

        movieEntityNode.setLocalPosition(MovieOffset)

    def returnItemSlot(self, ItemKey):
        InventoryItem = ItemManager.getItemInventoryItem(ItemKey)
        invEntity = self.getEntity()
        slot = invEntity.findSlot(InventoryItem)
        if slot is None:
            return

        if invEntity.inCursorItem(InventoryItem) is True:
            return

        CurrentSlotIndex = self.getParam("CurrentSlotIndex")
        inventoryItems = self.getParam("InventoryItems")
        index = CurrentSlotIndex + slot.slotId

        if len(inventoryItems) <= index:
            return

        cursorItem = ArrowManager.getArrowAttach()
        if cursorItem == InventoryItem:
            return

        InventoryItem.setPosition((0, 0))

        InventoryItemScale = DefaultManager.getDefaultFloat("InventoryItemScale", 1.0)
        InventoryItem.setScale((InventoryItemScale, InventoryItemScale, 1.0))

        slot.setItem(InventoryItem)

    def updateSlotsMovie(self, movieName, enable):
        if self.isActive() is False:
            return

        Entity = self.getEntity()
        Entity.updateSlotsMovie(movieName, enable)

    def addInventoryItem(self, InventoryItem):
        inventoryItems = self.getInventoryItems()
        if InventoryItem in inventoryItems:
            return

        self.appendParam("InventoryItems", InventoryItem)

    def removeItem(self, itemName):
        InventoryItem = ItemManager.getItemInventoryItem(itemName)
        self.removeInventoryItem(InventoryItem)

    def detachItem(self, InventoryItem):
        entity = self.getEntity()
        entity.inventoryGlobalMouseEvent(False)

        Notification.notify(Notificator.onInventoryUpdateItem)

    def removeInventoryItem(self, InventoryItem):
        InventoryItems = self.getParam("InventoryItems")

        if InventoryItem not in InventoryItems:
            return

        self.delParam("InventoryItems", InventoryItem)

    def removeAllItem(self):
        InventoryItems = self.getInventoryItems()

        for InventoryItem in InventoryItems:
            InventoryItem.setEnable(False)
            InventoryItem.setFoundItems([])

        self.setInventoryItems([])
        self.setCurrentSlotIndex(0)

    def getSlotID(self, InventoryItem):
        CurrentSlotIndex = self.getCurrentSlotIndex()
        InventoryItems = self.getInventoryItems()
        SlotCount = self.getSlotCount()

        InventoryItemIndex = InventoryItems.index(InventoryItem)

        SlotID = InventoryItemIndex - CurrentSlotIndex
        if 0 > SlotID >= SlotCount:
            return None

        return SlotID

    def getSlot(self, SlotID):
        Entity = self.getEntity()
        slot = Entity.getSlot(SlotID)
        return slot

    def hasInventoryItem(self, InventoryItem):
        InventoryItems = self.getInventoryItems()
        return InventoryItem in InventoryItems

    def indexInventoryItem(self, InventoryItem):
        InventoryItems = self.getInventoryItems()
        return InventoryItems.index(InventoryItem)

    def getFreeSlotID(self, inventoryItem):
        InventoryItems = self.getInventoryItems()
        SlotCount = self.getSlotCount()
        CurrentSlotIndex = self.getCurrentSlotIndex()

        if inventoryItem not in InventoryItems:
            InventoryItemCount = len(InventoryItems)
            CarriageIndex = int(InventoryItemCount / SlotCount) * SlotCount
            FreeSlotID = InventoryItemCount - CarriageIndex

            return FreeSlotID

        index = InventoryItems.index(inventoryItem)
        if index < CurrentSlotIndex:
            return 0
        if index > CurrentSlotIndex + SlotCount:
            return SlotCount - 1

        slotId = index - CurrentSlotIndex
        return slotId

    def getActiveSlots(self):
        InventoryItems = self.getInventoryItems()
        CurrentSlotIndex = self.getCurrentSlotIndex()
        SlotCount = self.getSlotCount()

        activeSlots = min(len(InventoryItems) - CurrentSlotIndex, SlotCount)

        return activeSlots

    def getScrollCountLeft(self, InventoryItem, needSlotIndex=None):
        CurrentSlotIndex = self.getParam("CurrentSlotIndex")
        InventoryItems = self.getParam("InventoryItems")
        SlotCount = self.getParam("SlotCount")

        if InventoryItem not in InventoryItems:
            InventoryItemIndex = self.getFreeSlotID(InventoryItem)
        else:
            InventoryItemIndex = InventoryItems.index(InventoryItem)

        activeSlotsCount = min(len(InventoryItems) - CurrentSlotIndex, SlotCount)

        if needSlotIndex is not None:
            CountLeft = CurrentSlotIndex - needSlotIndex
        else:
            CountLeft = InventoryItemIndex - CurrentSlotIndex - activeSlotsCount + 1

        return CountLeft

    def getScrollCountRight(self, InventoryItem, needSlotIndex=None):
        CurrentSlotIndex = self.getParam("CurrentSlotIndex")
        InventoryItems = self.getParam("InventoryItems")

        if InventoryItem not in InventoryItems:
            InventoryItemIndex = self.getFreeSlotID(InventoryItem)
        else:
            InventoryItemIndex = InventoryItems.index(InventoryItem)

        if needSlotIndex is not None:
            CountRight = CurrentSlotIndex - needSlotIndex
        else:
            CountRight = CurrentSlotIndex - InventoryItemIndex

        return CountRight
