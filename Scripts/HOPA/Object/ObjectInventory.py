from Foundation.ArrowManager import ArrowManager
from Foundation.DefaultManager import DefaultManager
from Foundation.Object.DemonObject import DemonObject
from HOPA.ItemManager import ItemManager
from Notification import Notification


class ObjectInventory(DemonObject):
    @staticmethod
    def declareORM(Type):
        DemonObject.declareORM(Type)

        Type.declareParam("CurrentSlotIndex")
        Type.declareParam("InventoryItems")
        Type.declareParam("SlotCount")
        Type.declareParam("SlotPolygon")
        Type.declareParam("SlotPoints")
        Type.declareParam("ItemReturn")
        pass

    def _onParams(self, params):
        super(ObjectInventory, self)._onParams(params)
        self.initParam("CurrentSlotIndex", params, 0)
        self.initParam("InventoryItems", params, [])
        self.initParam("SlotCount", params)
        self.initParam("SlotPolygon", params)
        self.initParam("SlotPoints", params)
        self.initParam("BlockScrolling", params, False)
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
        invEntity = self.getEntity()
        itemSlot = invEntity.findSlot(InvItem)
        itemSlot.point.addChild(movieEntity.node)

        # movieNode = movieEntity.getAnimatable()
        # movieSize = movieNode.getSize()
        # MovieOffset = (-(movieSize.x * 0.5), -(movieSize.y * 0.5))
        # movieEntity.node.setLocalPosition(MovieOffset)
        pass

    def returnItemSlot(self, ItemKey):
        InventoryItem = ItemManager.getItemInventoryItem(ItemKey)
        invEntity = self.getEntity()
        slot = invEntity.findSlot(InventoryItem)
        if slot is None:
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

        InventoryItemIndex = InventoryItems.index(InventoryItem)

        SlotID = InventoryItemIndex - CurrentSlotIndex
        if 0 > SlotID >= SlotCount:
            return None
            pass

        return SlotID
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

    def BlockButtons(self):
        if self.isActive():
            self.entity.ButtonBlock()

    def UnBlockButtons(self):
        if self.isActive():
            self.entity._updateButtonInteractive()
