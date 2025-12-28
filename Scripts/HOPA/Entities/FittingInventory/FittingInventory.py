from Foundation.ArrowManager import ArrowManager
from Foundation.DemonManager import DemonManager
from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.TaskManager import TaskManager
from Functor import Functor

class InventorySlot(object):
    def __init__(self, slotId, point, hotspot):
        #        self.inventoryObject = inventoryObject
        self.slotId = slotId
        self.point = point

        self.hotspot = hotspot

        self.item = None
        self.nodeBack = None
        pass

    def getPoint(self):
        return self.point
        pass

    def getHotSpot(self):
        return self.hotspot
        pass

    def setItem(self, item):
        self.item = item
        itemEntity = self.item.getEntity()
        itemEntity.inInventory()

        self.hotspot.setEventListener(onHandleMouseButtonEvent=self.__onMouseButtonEvent,
                                      onHandleMouseEnter=self.__onMouseEnter,
                                      onHandleMouseLeave=self.__onMouseLeave)
        self.hotspot.enable()

        self.nodeBack.enable()
        pass

    def removeItem(self):
        self.hotspot.setEventListener(onHandleMouseButtonEvent=None,
                                      onHandleMouseEnter=None,
                                      onHandleMouseLeave=None)
        self.hotspot.disable()
        self.nodeBack.disable()

        if self.item is None:
            Trace.log("Inventory", 0, "InventorySlot removeItem is Empty")
            return None
            pass

        itemEntity = self.item.getEntity()
        itemEntity.removeFromParent()

        self.item = None
        self.nodeBack = None
        pass

    def pickItem(self):
        if self.item is None:
            Trace.log("Inventory", 0, "InventorySlot pickItem is Empty")
            return None
            pass

        self.hotspot.disable()

        return self.item
        pass

    def returnItem(self):
        itemEntity = self.item.getEntity()
        itemEntity.inInventory()

        itemEntity.setLocalAlpha(1.0)
        spriteCenter = itemEntity.getSpriteCenter()
        hotspotCenter = self.hotspot.getLocalPolygonCenter()

        x = hotspotCenter.x - spriteCenter[0]
        y = hotspotCenter.y - spriteCenter[1]

        self.item.setPosition((x, y))

        self.point.addChild(itemEntity)

        self.hotspot.enable()
        pass

    def setFitting(self, item):
        self.item = item
        self.item.setEnable(True)

        FittingInventory = DemonManager.getDemon("FittingInventory")

        spriteBack = FittingInventory.getObject("Sprite_Fitting")
        spriteName = FittingInventory.getName()
        spriteResource = spriteBack.getParam("SpriteResourceName")

        self.nodeBack = Mengine.createSprite(spriteName, spriteResource)

        self.point.addChild(self.nodeBack)
        self.nodeBack.disable()

        self.returnItem()

        self.hotspot.disable()
        pass

    def __onMouseButtonEvent(self, context, event):
        if event.button != 0 or event.isDown is False:
            return False

        Notification.notify(Notificator.onInventoryItemClick, self.item)

        return False

    def __onMouseEnter(self, context, event):
        Notification.notify(Notificator.onInventoryItemMouseEnter, self.item)
        Notification.notify(Notificator.onInventorySlotItemEnter, self.object, self.item)

        return True
        pass

    def __onMouseLeave(self, context, event):
        Notification.notify(Notificator.onInventoryItemMouseLeave, self.item)
        Notification.notify(Notificator.onInventorySlotItemLeave, self.object, self.item)
        pass

    def getItem(self):
        return self.item
        pass

    def empty(self):
        return self.item is None
        pass

    def release(self):
        if self.item is not None:
            #            itemEntity = self.item.getEntity()
            #            itemEntity.removeFromParent()
            self.item = None
            pass

        if self.hotspot is not None:
            Mengine.destroyNode(self.hotspot)
            self.hotspot = None
            pass

        if self.nodeBack is not None:
            Mengine.destroyNode(self.nodeBack)
            self.nodeBack = None
            pass

        if self.point is not None:
            #            Mengine.destroyNode(self.point)
            self.point = None
            pass
        pass

    pass


class FittingInventory(BaseEntity):

    @staticmethod
    def declareORM(Type):
        BaseEntity.declareORM(Type)

        Type.addAction("InventoryItems",
                       Append=FittingInventory.__appendInventoryItems,
                       Remove=FittingInventory.__removeInventoryItems,
                       Change=FittingInventory.__changeInventoryItems)

        Type.addAction("Fittings",
                       Append=FittingInventory.__appendFittings,
                       Remove=FittingInventory.__removeFittings,
                       Change=FittingInventory.__changeFittings)

        Type.addAction("SlotCount")

        Type.addAction("SlotPoints")
        Type.addAction("SlotPolygon")

        Type.addAction("EnablePopUp")
        pass

    def __init__(self):
        super(FittingInventory, self).__init__()

        self.slots = []
        pass

    def getSlots(self):
        return self.slots
        pass

    def _onFinalize(self):
        super(FittingInventory, self)._onFinalize()

        for slot in self.slots:
            slot.release()
            pass

        self.slots = []
        pass

    def _onPreparation(self):
        self.setupPoints()
        pass

    def setupPoints(self):
        for index, point_position in enumerate(self.SlotPoints):
            slot = self.createSlot(index, point_position)
            self.slots.append(slot)
            pass
        pass

    def createSlot(self, Index, Position):
        spritePanel = self.object.getObject("Sprite_InventoryPanel")
        spritePanelEntity = spritePanel.getEntity()

        Sprite_Fitting = self.object.getObject("Sprite_Fitting")
        Sprite_Fitting.setEnable(False)

        panel_position = spritePanel.getPosition()
        panel_origin = spritePanel.getOrigin()

        leftTop = (panel_position[0] - panel_origin[0], panel_position[1] - panel_origin[1])

        point_node = spritePanelEntity.createChild("Point")

        delta = (Position[0] - leftTop[0], Position[1] - leftTop[1])
        point_node.setLocalPosition(delta)
        point_node.enable()

        hotspot_node = point_node.createChild("HotSpotPolygon")
        hotspot_node.setPolygon(self.SlotPolygon)
        hotspot_node.disable()

        slot = InventorySlot(Index, point_node, hotspot_node)
        return slot
        pass

    def _onActivate(self):
        super(FittingInventory, self)._onActivate()

        self.setEventListener(onGlobalHandleMouseButtonEventEnd=self.__onGlobalHandleMouseButtonEventEnd)

        self.updateSlots()

        Interaction_Inventory = self.object.getObject("Socket_Inventory")  # ("Interaction_Inventory")
        Interaction_Inventory.setParam("Interactive", 1)

        self.onFittingInventorySlotClickObserver = Notification.addObserver(Notificator.onFittingInventorySlotClick, self.__onFittingInventorySlotClick)
        self.onFittingInventorySlotUseObserver = Notification.addObserver(Notificator.onFittingInventorySlotUse, self.__onFittingInventorySlotUse)

        self.onFittingInventorySlotMouseEnterObserver = Notification.addObserver(Notificator.onFittingInventorySlotMouseEnter, self.__onFittingInventorySlotMouseEnter)
        self.onFittingInventorySlotMouseLeaveObserver = Notification.addObserver(Notificator.onFittingInventorySlotMouseLeave, self.__onFittingInventorySlotMouseLeave)
        pass

    def _onDeactivate(self):
        super(FittingInventory, self)._onDeactivate()

        self.inventoryGlobalMouseEvent(False)

        for slot in self.slots:
            slot.release()
            pass

        self.slots = []

        Notification.notify(Notificator.onSlotMouseLeave)

        Notification.removeObserver(self.onFittingInventorySlotClickObserver)
        Notification.removeObserver(self.onFittingInventorySlotUseObserver)

        Notification.removeObserver(self.onFittingInventorySlotMouseEnterObserver)
        Notification.removeObserver(self.onFittingInventorySlotMouseLeaveObserver)
        pass

    def __onFittingInventorySlotClick(self, slotId):
        self.pickInventoryItem(slotId)

        return False
        pass

    def __onFittingInventorySlotUse(self, slotId):
        self.combineInventoryItem(slotId)

        return False
        pass

    def __onFittingInventorySlotMouseEnter(self, slotId):
        slot = self.slots[slotId]

        if slot.item is not None:
            Notification.notify(Notificator.onInventoryItemMouseEnter, self.object, slot.item)
            pass

        return False
        pass

    def __onFittingInventorySlotMouseLeave(self, slotId):
        slot = self.slots[slotId]

        if slot.item is not None:
            Notification.notify(Notificator.onInventoryItemMouseLeave, slot.item)
            Notification.notify(Notificator.onInventorySlotItemLeave, self.object, self.item)
            pass

        return False
        pass

    def __onGlobalHandleMouseButtonEventEnd(self, touchId, x, y, button, pressure, isDown, isPressed):
        if button != 0 or isDown is False:
            return True
            pass

        if ArrowManager.emptyArrowAttach() is True:
            self.inventoryGlobalMouseEvent(False)
            return True

        InventoryItem = ArrowManager.getArrowAttach()
        InventoryItemEntity = InventoryItem.getEntity()

        state = InventoryItemEntity.getState()

        if state is InventoryItemEntity.ITEM_PICK:
            TaskManager.runAlias("AliasFittingInventoryInvalidUseInventoryItem", self.__updateInventoryItem, FittingInventory=self.object)

            self.inventoryGlobalMouseEvent(False)
        elif state is InventoryItemEntity.ITEM_RETURN:
            TaskManager.runAlias("AliasFittingInventoryReturnInventoryItem", self.__updateInventoryItem, FittingInventory=self.object)

            self.inventoryGlobalMouseEvent(False)
        elif state is InventoryItemEntity.ITEM_TAKE:
            TaskManager.runAlias("AliasFittingInventoryRemoveInventoryItem", self.__updateInventoryItem, FittingInventory=self.object, InventoryItem=InventoryItem)

            self.inventoryGlobalMouseEvent(False)

        elif state is InventoryItemEntity.ITEM_PLACE:
            InventoryItemEntity.pickAfterPlace()

            self.__updateInventoryItem(False)
        elif state is InventoryItemEntity.ITEM_TRY_COMBINE:
            TaskManager.runAlias("AliasFittingInventoryInvalidCombineInventoryItem", self.__updateInventoryItem, FittingInventory=self.object)

            self.inventoryGlobalMouseEvent(False)
        elif state is InventoryItemEntity.ITEM_COMBINE:
            self.inventoryGlobalMouseEvent(False)

            self.__updateInventoryItem(False)
            pass

        return True
        pass

    def __updateInventoryItem(self, isSkip):
        Notification.notify(Notificator.onInventoryUpdateItem)
        pass

    def inventoryGlobalMouseEvent(self, value):
        self.enableGlobalMouseEvent(value)
        pass

    def pickInventoryItem(self, slotId):
        slot = self.slots[slotId]
        InventoryItem = slot.pickItem()

        ArrowManager.attachArrow(InventoryItem)
        self.inventoryGlobalMouseEvent(True)

        itemNode = Mengine.getArrowNode()

        InventoryItemEntity = InventoryItem.getEntity()
        InventoryItemEntity.pick()

        itemNode.addChild(InventoryItemEntity)

        TaskManager.runAlias("AliasInventoryPickInventoryItem", Functor(self._pickInventoryItem, InventoryItem), InventoryItem=InventoryItem)
        pass

    def combineInventoryItem(self, slotId):
        slot = self.slots[slotId]
        if slot.item is None:
            return

        InventoryItem = ArrowManager.getArrowAttach()

        InventoryItemEntity = InventoryItem.getEntity()

        if hasattr(InventoryItemEntity, "tryCombine") is False:
            return
            pass

        InventoryItemEntity.tryCombine()

        Notification.notify(Notificator.onInventoryCombineInventoryItem, self.object, InventoryItem, slot.item)
        pass

    def _pickInventoryItem(self, isSkip, InventoryItem):
        Notification.notify(Notificator.onInventoryPickInventoryItem, self.object, InventoryItem)
        pass

    def updateSlots(self):
        Fittings = self.object.getParam("Fittings")

        for Index, InventoryItem in Fittings:
            slot = self.slots[Index]
            slot.setFitting(InventoryItem)
            pass

        InventoryItems = self.object.getParam("InventoryItems")

        for Index, InventoryItem in InventoryItems:
            slot = self.slots[Index]
            slot.setItem(InventoryItem)
            pass
        pass

    def __appendInventoryItems(self, id, item):
        Index, InventoryItem = item

        slot = self.slots[Index]
        slot.setItem(InventoryItem)
        pass

    def __changeInventoryItems(self, id, item):
        self.inventoryGlobalMouseEvent(False)
        pass

    def __removeInventoryItems(self, id, item, Items):
        pass

    def __appendFittings(self, id, fitting):
        Index, InventoryItem = fitting

        slot = self.slots[Index]

        slot.setFitting(InventoryItem)
        pass

    def __changeFittings(self, id, fitting):
        self.inventoryGlobalMouseEvent(False)
        pass

    def __removeFittings(self, id, fitting, Fittings):
        pass

    pass
