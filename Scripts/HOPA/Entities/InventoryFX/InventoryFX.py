from Foundation.ArrowManager import ArrowManager
from Foundation.DefaultManager import DefaultManager
from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.GroupManager import GroupManager
from Foundation.PolicyManager import PolicyManager
from Foundation.SystemManager import SystemManager
from Foundation.TaskManager import TaskManager
from HOPA.ItemManager import ItemManager
from Notification import Notification

class InventorySlot(object):
    def __init__(self, inventoryObject, slotId, slot, hotspot):
        self.inventoryObject = inventoryObject
        self.slotId = slotId
        self.slot = slot
        self.hotspot = hotspot

        self.item = None
        self.cursorItem = None
        self.removeItem2 = None
        self.hide = False

        self.point = slot
        self.scaleTo = 1
        pass

    def _onMouseEnter(self, x, y):
        Notification.notify(Notificator.onInventoryItemMouseEnter, self.item)
        Notification.notify(Notificator.onInventorySlotItemEnter, self.inventoryObject, self.item)
        return True
        pass

    def _onMouseLeave(self):
        removeItem = self.item or self.cursorItem or self.removeItem2

        Notification.notify(Notificator.onInventoryItemMouseLeave, removeItem)
        Notification.notify(Notificator.onInventorySlotItemLeave, self.inventoryObject, removeItem)
        pass

    def _onMouseButtonEvent(self, touchId, x, y, button, pressure, isDown, isPressed):
        if button != 0 or isDown is False:
            return True
            pass

        ################FIX for Item plus

        Name = ItemManager.getInventoryItemKey(self.item)
        itemInManager = ItemManager.getItem(Name)
        ScenePlus = itemInManager.PlusScene
        if (ScenePlus is not None):
            GroupZoom = GroupManager.getGroup(ScenePlus)
            Notification.notify(Notificator.onItemZoomEnter, GroupZoom, ScenePlus)
            return True
            pass
        ##################################

        Notification.notify(Notificator.onInventoryPickInventoryItem, self.item)

        InventoryEntity = self.inventoryObject.getEntity()

        if ArrowManager.emptyArrowAttach() is True:
            InventoryEntity.pickInventoryItem(self.slotId)
        else:
            if self.item is None:
                return True
                pass

            InventoryEntity.combineInventoryItem(self.slotId)
            pass

        return True
        pass

    def getPoint(self):
        return self.point
        pass

    def getHotSpot(self):
        return self.hotspot
        pass

    def getPointCameraPosition(self, Camera):
        return Mengine.getCameraPosition(Camera, self.point)
        pass

    def getItemOffset(self):
        itemEntity = self.item.getEntity()

        itemSlotPoint = self.item.getSlotPoint()
        if itemSlotPoint is None:
            itemSlotPoint = itemEntity.getSpriteCenter()
            pass

        hotspotWordCenter = self.hotspot.getWorldPolygonCenter()
        slotWordPos = self.slot.getWorldPosition()

        x = (hotspotWordCenter.x - slotWordPos.x - itemSlotPoint[0] * self.scaleTo)
        y = (hotspotWordCenter.y - slotWordPos.y - itemSlotPoint[1] * self.scaleTo)

        return (x, y)
        pass

    def setItem(self, item):
        self.item = item

        if self.slot is None or self.hotspot is None:
            return
            pass

        self.cursorItem = None
        self.removeItem2 = None

        if self.hide is True:
            self.item.setEnable(False)
            pass
        else:
            self.item.setEnable(True)
            self.slot.compile()
            self.hotspot.enable()
            self.hotspot.compile()
            pass

        itemEntity = self.item.getEntity()

        sprite = itemEntity.getSprite()
        size = sprite.getSurfaceSize()

        InventoryItemsScaleSlot = DefaultManager.getDefaultBool("InventoryItemsScaleSlot", True)
        if InventoryItemsScaleSlot is True:
            InventorySlotSize = DefaultManager.getDefaultFloat("InventorySlotSize", 70)
            scaleToX = InventorySlotSize / size.x
            scaleToY = InventorySlotSize / size.y
            self.scaleTo = min(scaleToX, scaleToY)
            pass

        InventoryItemsStaticScale = DefaultManager.getDefaultBool("InventoryItemsStaticScale", False)
        if InventoryItemsStaticScale is True:
            self.scaleTo = DefaultManager.getDefaultFloat("InventoryItemScale", 1)
            pass

        item.setScale((self.scaleTo, self.scaleTo, 1.0))

        itemEntity.inInventory()
        itemPosition = self.getItemOffset()
        self.item.setPosition(itemPosition)

        itemEntityNode = self.item.getEntityNode()

        self.slot.addChild(itemEntityNode)

        self.hotspot.setEventListener(onHandleMouseEnter=self._onMouseEnter, onHandleMouseLeave=self._onMouseLeave, onHandleMouseButtonEvent=self._onMouseButtonEvent)
        pass

    def removeItem(self):
        if self.cursorItem is None and self.item is None:
            Trace.log("Inventory", 0, "InventorySlot removeItem is Empty")
            return None
            pass

        self.removeItem2 = self.item or self.cursorItem

        self.item = None
        self.cursorItem = None

        # removeItemEntity = removeItem.getEntity()
        # removeItemEntity.removeFromParent()

        self.removeItem2.returnToParent()

        self.hotspot.disable()

        return self.removeItem2
        pass

    def returnItem(self):
        if self.item is None:
            Trace.log("Inventory", 0, "InventorySlot returnItem is Empty")
            return None
            pass

        self.cursorItem = self.item

        self.item = None
        self.removeItem2 = None

        removeItemEntity = self.cursorItem.getEntity()
        removeItemEntity.removeFromParent()

        self.hotspot.disable()

        return self.cursorItem
        pass

    def getItem(self):
        return self.item
        pass

    def getCursorItem(self):
        return self.cursorItem
        pass

    def empty(self):
        return self.item is None
        pass

    def getSlotID(self):
        return self.slotId
        pass

    def changeSlot(self, slot, enable):
        if self.hotspot is None:
            return
            pass

        self.slot = slot
        self.hide = False
        if self.item is not None:
            itemEntity = self.item.getEntity()
            itemEntityNode = self.item.getEntityNode()

            self.slot.addChild(itemEntityNode)

            if enable is False:
                # self.hotspot.disable()
                pass
            else:
                itemPosition = self.getItemOffset()

                self.item.setPosition(itemPosition)
                self.item.setEnable(True)

                self.hotspot.setEventListener(onHandleMouseEnter=self._onMouseEnter, onHandleMouseLeave=self._onMouseLeave, onHandleMouseButtonEvent=self._onMouseButtonEvent)
                self.hotspot.enable()
                pass
            pass
        else:
            if enable is False:
                self.hide = True
                pass
            pass
        pass

    def release(self):
        self.cursorItem = None
        self.removeItem2 = None
        self.hotspot = None

        if self.item is not None:
            itemEntity = self.item.getEntity()
            itemEntity.removeFromParent()

            self.item = None
            pass

        self.slot = None
        self.inventoryObject = None
        pass
    pass

class InventoryFX(BaseEntity):

    @staticmethod
    def declareORM(Type):
        BaseEntity.declareORM(Type)

        Type.addActionActivate(Type, "InventoryItems", Append=InventoryFX._appendInventoryItems, Remove=InventoryFX._removeInventoryItems)

        Type.addAction(Type, "SlotPoints")
        Type.addAction(Type, "SlotCount")
        Type.addActionActivate(Type, "CurrentSlotIndex", Update=InventoryFX._updateCurrentSlotIndex)

        Type.addAction(Type, "SlotPolygon")
        pass

    def __init__(self):
        super(InventoryFX, self).__init__()

        self.slots = []

        self.onInventoryAttachInvItemToArrowObserver = None
        self.onAccountFinalizeObserver = None
        pass

    def _onPreparation(self):
        SlotCount = DefaultManager.getDefaultInt("InventorySlotCount", 7)
        self.object.setSlotCount(SlotCount)
        self.setupPoints()

        if SystemManager.hasSystem("SystemItemPlusScene") is False:
            return False
            pass

        SystemItemPlus = SystemManager.getSystem("SystemItemPlusScene")

        if (SystemItemPlus is not None):
            SystemItemPlus.InitExtra()
            pass
        pass

    def getSlots(self):
        return self.slots
        pass

    def __detachItemToArrow(self, invItem):
        slotID = self.object.getSlotID(invItem)
        self.pickInventoryItem(slotID)
        self.inventoryGlobalMouseEvent(True)
        return False
        pass

    def _onGlobalHandleMouseButtonEventEnd(self, event):
        if event.button != 0 or event.isDown is False:
            return
            pass

        if ArrowManager.emptyArrowAttach() is True:
            self.inventoryGlobalMouseEvent(False)
            return

        if event.button == 0 and event.isDown is True:
            InventoryItem = ArrowManager.getArrowAttach()
            # self.__detachInventoryItem(InventoryItem)
            if InventoryItem in self.InventoryItems:
                self.__detachInventoryItem(InventoryItem)
                pass
            else:
                self.inventoryGlobalMouseEvent(False)
                pass
            pass

        return
        pass

    def __detachInventoryItem(self, InventoryItem):
        InventoryItemEntity = InventoryItem.getEntity()

        state = InventoryItemEntity.getState()
        PolicyPickInventoryItemEnd = PolicyManager.getPolicy("PickInventoryItemEnd", "PolicyPickInventoryItemEffectDummy")
        PolicyPickInventoryItemStop = PolicyManager.getPolicy("PickInventoryItemStop", "PolicyPickInventoryItemEffectDummy")

        if state is InventoryItemEntity.ITEM_PICK:  # state 2
            with TaskManager.createTaskChain(Group=self.object) as tc:
                tc.addTask("TaskFunction", Fn=self.inventoryGlobalMouseEvent, Args=(False,))
                tc.addTask("AliasInventoryInvalidUseInventoryItemFX", Inventory=self.object)
                tc.addTask("TaskFunction", Fn=self._updateInventoryItem)

                tc.addTask(PolicyPickInventoryItemEnd, InventoryItem=InventoryItem)
                pass
            pass

        elif state is InventoryItemEntity.ITEM_RETURN:  # state 3
            with TaskManager.createTaskChain(Group=self.object) as tc:
                tc.addTask("TaskFunction", Fn=self.inventoryGlobalMouseEvent, Args=(False,))
                tc.addTask("AliasInventoryReturnInventoryItemFX", Inventory=self.object)
                tc.addTask("TaskFunction", Fn=self._updateInventoryItem)

                tc.addTask(PolicyPickInventoryItemEnd, InventoryItem=InventoryItem)
                pass
            pass

        elif state is InventoryItemEntity.ITEM_TAKE:  # state 5
            with TaskManager.createTaskChain(Group=self.object) as tc:
                tc.addTask("TaskFunction", Fn=self.inventoryGlobalMouseEvent, Args=(False,))
                tc.addTask("AliasInventoryRemoveInventoryItemFX", Inventory=self.object, InventoryItem=InventoryItem)
                tc.addTask("TaskFunction", Fn=self._updateInventoryItem)

                tc.addTask(PolicyPickInventoryItemStop, InventoryItem=InventoryItem)
                pass
            pass

        elif state is InventoryItemEntity.ITEM_PLACE:  # state 4
            with TaskManager.createTaskChain(Group=self.object) as tc:
                tc.addTask(PolicyPickInventoryItemStop, InventoryItem=InventoryItem)
                pass

            InventoryItemEntity.pickAfterPlace()
            self._updateInventoryItem()
            pass

        elif state is InventoryItemEntity.ITEM_TRY_COMBINE:
            with TaskManager.createTaskChain(Group=self.object) as tc:
                tc.addTask("TaskFunction", Fn=self.inventoryGlobalMouseEvent, Args=(False,))
                tc.addTask("AliasInventoryReturnInventoryItemFX", Inventory=self.object)
                tc.addTask("TaskFunction", Fn=self._updateInventoryItem)

                tc.addTask(PolicyPickInventoryItemEnd, InventoryItem=InventoryItem)
                pass
            pass

        elif state is InventoryItemEntity.ITEM_COMBINE:
            with TaskManager.createTaskChain(Group=self.object) as tc:
                tc.addTask("TaskFunction", Fn=self._updateInventoryItem)

                tc.addTask(PolicyPickInventoryItemStop, InventoryItem=InventoryItem)
                pass

            self.inventoryGlobalMouseEvent(False)
            pass
        pass

    def _updateInventoryItem(self):
        Notification.notify(Notificator.onInventoryUpdateItem)
        pass

    def _updateCurrentSlotIndex(self, CurrentSlotIndex):
        Notification.notify(Notificator.onInventoryCurrentSlotIndex, self.object)
        if len(self.InventoryItems) == self.SlotCount and CurrentSlotIndex != 0:
            self.object.setCurrentSlotIndex(0)
            return
            pass
        pass

    def inventoryGlobalMouseEvent(self, value):
        Mengine.enableGlobalHandler(self.MouseButtonHandlerID, value)
        # self.enableGlobalMouseEvent(value)
        pass

    def pickInventoryItem(self, slotId):
        if slotId not in range(len(self.slots)):
            Trace.log("Inventory", 0, "InvetoryFX.pickInventoryItem: slotId %d not in range self.slots %d" % (slotId, len(self.slots)))
            return
            pass

        slot = self.slots[slotId]

        InventoryItem = slot.returnItem()

        ArrowManager.attachArrow(InventoryItem)

        with TaskManager.createTaskChain() as tc:
            tc.addTask("TaskMouseButtonClick")
            tc.addTask("TaskFunction", Fn=self.inventoryGlobalMouseEvent, Args=(True,))
            pass

        arrow = ArrowManager.getArrow()

        InventoryItemEntity = InventoryItem.getEntity()
        InventoryItemEntityNode = InventoryItem.getEntityNode()
        InventoryItemEntity.pick()
        # InventoryItem.setScale( (1.0, 1.0, 1.0) )

        arrow.addChildFront(InventoryItemEntityNode)

        PickInventoryItem = PolicyManager.getPolicy("PickInventoryItem", "TaskEffectInventoryPickInventoryItem")
        TaskManager.runAlias(PickInventoryItem, None, InventoryItem=InventoryItem)

        # -- fix for item drop
        self.inventoryGlobalMouseEvent(False)
        # --
        pass

    def combineInventoryItem(self, slotId):
        slot = self.slots[slotId]

        InventoryItem = ArrowManager.getArrowAttach()
        InventoryItemEntity = InventoryItem.getEntity()
        InventoryItemEntity.tryCombine()

        Notification.notify(Notificator.onInventoryCombineInventoryItem, self.object, InventoryItem, slot.item)
        pass

    def setupPoints(self):
        Movie_Slots = self.object.getObject("Movie_Slots")
        Movie_SlotsEntity = Movie_Slots.getEntity()

        for index in xrange(self.SlotCount):
            slot = Movie_SlotsEntity.getMovieSlot("%s" % (str(index)))
            socket = Movie_SlotsEntity.getSocket("slot%s" % (str(index)))
            socket.disable()

            slot = InventorySlot(self.object, index, slot, socket)
            self.slots.append(slot)
            pass
        pass

    def updateSlotsMovie(self, movieName, enable):
        Movie = self.object.getObject(movieName)
        MovieEntity = Movie.getEntity()

        activeslots = self.object.getActiveSlots()

        for index in range(0, activeslots):
            slot = self.slots[index]
            movieSlot = MovieEntity.getMovieSlot("%s" % (str(index)))
            slot.changeSlot(movieSlot, enable)
            pass
        pass

    def _onActivate(self):
        super(InventoryFX, self)._onActivate()

        # self.setEventListener(onGlobalHandleMouseButtonEventEnd = self._onGlobalHandleMouseButtonEventEnd)
        self.MouseButtonHandlerID = Mengine.addMouseButtonHandlerEnd(self._onGlobalHandleMouseButtonEventEnd)
        Mengine.enableGlobalHandler(self.MouseButtonHandlerID, False)

        self.updateSlots()

        self.onInventoryAttachInvItemToArrowObserver = Notification.addObserver(Notificator.onInventoryDetachInvItemToArrow, self.__detachItemToArrow)
        self.onAccountFinalizeObserver = Notification.addObserver(Notificator.onAccountFinalize, self.__onAccountFinalize)

        Notification.notify(Notificator.onInventoryActivate, self.object)
        pass

    def __onAccountFinalize(self):
        Notification.notify(Notificator.onInventoryUpdateItem)

        return False
        pass

    def removeSlots(self):
        for slot in self.slots:
            slot.release()
            pass
        self.slots = []
        pass

    def _onDeactivate(self):
        super(InventoryFX, self)._onDeactivate()

        def __returnInvItemForce(InventoryItem):
            PolicyPickInventoryItemStop = PolicyManager.getPolicy("PickInventoryItemStop", "PolicyPickInventoryItemEffectDummy")
            TaskManager.runAlias(PolicyPickInventoryItemStop, None)
            TaskManager.runAlias("TaskInventorySlotReturnItem", None, InventoryItem=InventoryItem, Inventory=self.object)
            TaskManager.runAlias("TaskObjectReturn", None, Object=InventoryItem)
            pass

        if ArrowManager.emptyArrowAttach() is False:
            InventoryItem = ArrowManager.getArrowAttach()
            hasInventoryItem = self.object.hasInventoryItem(InventoryItem)
            if hasInventoryItem is True:
                __returnInvItemForce(InventoryItem)
                pass
            pass

        for slot in self.slots:
            slotCursorItem = slot.getCursorItem()
            if slotCursorItem is not None:
                __returnInvItemForce(slotCursorItem)
                pass
            pass

        self.removeSlots()

        # self.inventoryGlobalMouseEvent(False)
        # self.setEventListener(onGlobalHandleMouseButtonEventEnd = None)

        Mengine.removeGlobalHandler(self.MouseButtonHandlerID)
        self.MouseButtonHandlerID = None

        Notification.notify(Notificator.onInventoryDeactivate, self.object)

        Notification.removeObserver(self.onInventoryAttachInvItemToArrowObserver)
        Notification.removeObserver(self.onAccountFinalizeObserver)
        pass

    def updateSlots(self):
        Movie_Slots = self.object.getObject("Movie_Slots")
        Movie_SlotsEntity = Movie_Slots.getEntity()
        MovieNode = Movie_SlotsEntity.getAnimatable()
        MovieNode.compile()

        for InventoryItem in self.InventoryItems:
            InventoryItem.setEnable(False)
            pass

        activeSlot = self.object.getActiveSlots()

        for i in xrange(activeSlot):
            slot = self.slots[i]
            InventoryItem = self.InventoryItems[self.CurrentSlotIndex + i]

            slot.setItem(InventoryItem)
            pass
        pass

    def _appendInventoryItems(self, id, inventoryItem):
        slot = self.findSlot(inventoryItem)

        Notification.notify(Notificator.onInventoryAppendInventoryItem, inventoryItem)

        if slot is None:
            return
            pass

        slot.setItem(inventoryItem)
        pass

    def _removeInventoryItems(self, id, inventoryItem, inventoryItems):
        slot = self.findSlot(inventoryItem)

        if slot is not None:
            slot.removeItem()
            pass

        Notification.notify(Notificator.onInventoryRemoveItem, inventoryItem)
        pass

    def getSlot(self, index):
        if len(self.slots) <= index:
            return None
        return self.slots[index]
        pass

    def inCursorItem(self, inventoryItem):
        for slot in self.slots:
            cursorItem = slot.getCursorItem()
            if cursorItem is inventoryItem:
                return True
                pass
            pass

        return False
        pass

    def findSlot(self, inventoryItem):
        if inventoryItem is None:
            return None
            pass

        for slot in self.slots:
            item = slot.getItem()
            if item is inventoryItem:
                return slot
                pass

            cursorItem = slot.getCursorItem()
            if cursorItem is inventoryItem:
                return slot
                pass
            pass

        slotID = self.object.getFreeSlotID(inventoryItem)
        if slotID >= len(self.slots):
            return None
            pass
        slot = self.slots[slotID]
        return slot
        pass

    def findSlotID(self, inventoryItem):
        for slot in self.slots:
            item = slot.getItem()
            if item is inventoryItem:
                return self.slots.index(slot)
                pass

            cursorItem = slot.getCursorItem()
            if cursorItem is inventoryItem:
                return self.slots.index(slot)
                pass
            pass

        return None
        pass

    pass