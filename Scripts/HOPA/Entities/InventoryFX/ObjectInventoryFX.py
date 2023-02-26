from Foundation.ArrowManager import ArrowManager
from Foundation.DefaultManager import DefaultManager
from Foundation.Object.DemonObject import DemonObject
from HOPA.ItemManager import ItemManager
from Notification import Notification

class ObjectInventoryFX(DemonObject):
    @staticmethod
    def declareORM(Type):
        DemonObject.declareORM(Type)

        Type.addParam(Type, "CurrentSlotIndex")
        Type.addParam(Type, "InventoryItems")
        Type.addParam(Type, "SlotCount")
        Type.addParam(Type, "SlotPolygon")
        Type.addParam(Type, "SlotPoints")
        pass

    def _onParams(self, params):
        super(ObjectInventoryFX, self)._onParams(params)
        self.initParam("CurrentSlotIndex", params, 0)
        self.initParam("InventoryItems", params, [])
        self.initParam("SlotCount", params, 0)
        self.initParam("SlotPolygon", params, None)
        self.initParam("SlotPoints", params, None)
        pass

    def addItem(self, itemName):
        InventoryItem = ItemManager.getItemInventoryItem(itemName)

        self.addInventoryItem(InventoryItem)
        pass

    def getInventoryItem(self, itemName):
        InventoryItem = ItemManager.getItemInventoryItem(itemName)
        return InventoryItem
        pass

    def getInventoryItemKey(self, invItem):
        ItemKey = ItemManager.getInventoryItemKey(invItem)
        return ItemKey
        pass

    def getItemTextID(self, itemName):
        textID = ItemManager.getTextID(itemName)
        return textID
        pass

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
        pass

    def returnItemSlot(self, ItemKey):
        InventoryItem = ItemManager.getItemInventoryItem(ItemKey)
        invEntity = self.getEntity()
        slot = invEntity.findSlot(InventoryItem)
        if slot is None:
            return
            pass

        if invEntity.inCursorItem(InventoryItem) is True:
            return
            pass

        CurrentSlotIndex = self.getParam("CurrentSlotIndex")
        inventoryItems = self.getParam("InventoryItems")
        index = CurrentSlotIndex + slot.slotId

        if len(inventoryItems) <= index:
            return
            pass

        cursorItem = ArrowManager.getArrowAttach()
        if cursorItem == InventoryItem:
            return
            pass

        InventoryItem.setPosition((0, 0))

        InventoryItemScale = DefaultManager.getDefaultFloat("InventoryItemScale", 1.0)
        InventoryItem.setScale((InventoryItemScale, InventoryItemScale, 1.0))

        slot.setItem(InventoryItem)
        pass

    def updateSlotsMovie(self, movieName, enable):
        if self.isActive() is False:
            return
            pass

        Entity = self.getEntity()
        Entity.updateSlotsMovie(movieName, enable)
        pass

    def addInventoryItem(self, InventoryItem):
        inventoryItems = self.getInventoryItems()

        if InventoryItem in inventoryItems:
            return
            pass

        self.appendParam("InventoryItems", InventoryItem)
        pass

    def removeItem(self, itemName):
        InventoryItem = ItemManager.getItemInventoryItem(itemName)

        self.removeInventoryItem(InventoryItem)
        pass

    def detachItem(self, InventoryItem):
        entity = self.getEntity()
        entity.inventoryGlobalMouseEvent(False)

        Notification.notify(Notificator.onInventoryUpdateItem)
        pass

    def removeInventoryItem(self, InventoryItem):
        InventoryItems = self.getParam("InventoryItems")

        if InventoryItem not in InventoryItems:
            return
            pass

        self.delParam("InventoryItems", InventoryItem)
        pass

    def removeAllItem(self):
        InventoryItems = self.getInventoryItems()

        for InventoryItem in InventoryItems:
            InventoryItem.setEnable(False)
            InventoryItem.setFoundItems([])
            pass

        self.setInventoryItems([])
        self.setCurrentSlotIndex(0)
        pass

    def getSlotID(self, InventoryItem):
        CurrentSlotIndex = self.getCurrentSlotIndex()
        InventoryItems = self.getInventoryItems()
        SlotCount = self.getSlotCount()

        InventoryItemIndex = InventoryItems.index(InventoryItem)

        SlotID = InventoryItemIndex - CurrentSlotIndex
        if 0 > SlotID >= SlotCount:
            return None
            pass

        return SlotID
        pass

    def getSlot(self, SlotID):
        Entity = self.getEntity()
        slot = Entity.getSlot(SlotID)

        return slot
        pass

    def hasInventoryItem(self, InventoryItem):
        InventoryItems = self.getInventoryItems()

        return InventoryItem in InventoryItems
        pass

    def hasInventoryItem(self, InventoryItem):
        InventoryItems = self.getInventoryItems()

        return InventoryItem in InventoryItems
        pass

    def indexInventoryItem(self, InventoryItem):
        InventoryItems = self.getInventoryItems()

        return InventoryItems.index(InventoryItem)
        pass

    def getFreeSlotID(self, inventoryItem):
        InventoryItems = self.getInventoryItems()
        SlotCount = self.getSlotCount()
        CurrentSlotIndex = self.getCurrentSlotIndex()

        if inventoryItem not in InventoryItems:
            InventoryItemCount = len(InventoryItems)
            CarriageIndex = int(InventoryItemCount / SlotCount) * SlotCount
            FreeSlotID = InventoryItemCount - CarriageIndex

            return FreeSlotID
            pass

        index = InventoryItems.index(inventoryItem)
        if index < CurrentSlotIndex:
            return 0
            pass

        if index > CurrentSlotIndex + SlotCount:
            return SlotCount - 1
            pass

        slotId = index - CurrentSlotIndex

        return slotId
        pass

    def getActiveSlots(self):
        InventoryItems = self.getInventoryItems()
        CurrentSlotIndex = self.getCurrentSlotIndex()
        SlotCount = self.getSlotCount()

        activeSlots = min(len(InventoryItems) - CurrentSlotIndex, SlotCount)

        return activeSlots
        pass

    def getScrollCountLeft(self, InventoryItem, needSlotIndex=None):
        CurrentSlotIndex = self.getParam("CurrentSlotIndex")
        InventoryItems = self.getParam("InventoryItems")
        SlotCount = self.getParam("SlotCount")

        if InventoryItem not in InventoryItems:
            InventoryItemIndex = self.getFreeSlotID(InventoryItem)
            pass
        else:
            InventoryItemIndex = InventoryItems.index(InventoryItem)
            pass

        activeSlotsCount = min(len(InventoryItems) - CurrentSlotIndex, SlotCount) \
 \
            if needSlotIndex is not None:
                CountLeft = CurrentSlotIndex - needSlotIndex
                pass

            else:
                CountLeft = InventoryItemIndex - CurrentSlotIndex - activeSlotsCount + 1
                pass

        return CountLeft
        pass

    def getScrollCountRight(self, InventoryItem, needSlotIndex=None):
        CurrentSlotIndex = self.getParam("CurrentSlotIndex")
        InventoryItems = self.getParam("InventoryItems")

        if InventoryItem not in InventoryItems:
            InventoryItemIndex = self.getFreeSlotID(InventoryItem)
            pass
        else:
            InventoryItemIndex = InventoryItems.index(InventoryItem)
            pass

        if needSlotIndex is not None:
            CountRight = CurrentSlotIndex - needSlotIndex
            pass

        else:
            CountRight = CurrentSlotIndex - InventoryItemIndex
            pass

        return CountRight
        pass

    pass