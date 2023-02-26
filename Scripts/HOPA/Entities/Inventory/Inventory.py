import Trace
from Foundation.ArrowManager import ArrowManager
from Foundation.DefaultManager import DefaultManager
from Foundation.GroupManager import GroupManager
from Foundation.Notificator import Notificator
from Foundation.PolicyManager import PolicyManager
from Foundation.Task.Semaphore import Semaphore
from Foundation.TaskManager import TaskManager
from HOPA.Entities.InventoryBase import InventoryBase
from HOPA.ItemManager import ItemManager
from Notification import Notification

InventoryBase = Mengine.importEntity("InventoryBase")

class InventorySlot(object):
    def __init__(self, inventoryObject, slotId, point, hotspot):
        self.inventoryObject = inventoryObject
        self.slotId = slotId
        self.point = point
        self.hotspot = hotspot

        self.item = None
        self.cursorItem = None

        self.block = False

    def _onMouseEnter(self, _x, _y):
        if Mengine.hasTouchpad() is True:
            return True  # If player set cursor via touchpad over item - it will play effects - we need to block it
        Notification.notify(Notificator.onInventoryItemMouseEnter, self.item)
        Notification.notify(Notificator.onInventorySlotItemEnter, self.inventoryObject, self.item)
        return True

    def _onMouseLeave(self):
        if Mengine.hasTouchpad() is True:
            return True  # If player set cursor via touchpad over item - it will play effects - we need to block it
        Notification.notify(Notificator.onInventoryItemMouseLeave, self.item)
        Notification.notify(Notificator.onInventorySlotItemLeave, self.inventoryObject, self.item)

    def _onHandleMouseOverDestroy(self):
        if Mengine.hasTouchpad() is True:
            return True  # If player set cursor via touchpad over item - it will play effects - we need to block it
        Notification.notify(Notificator.onInventoryItemMouseLeave, self.item)
        Notification.notify(Notificator.onInventorySlotItemLeave, self.inventoryObject, self.item)

    def _onMouseButtonEvent(self, _touchId, _x, _y, button, _pressure, isDown, _isPressed):
        if button != 0 or isDown is False:
            return True

        if self.block is True:
            return True

        # FIX for Item plus _______________________________________________________
        Name = ItemManager.getInventoryItemKey(self.item)
        itemInManager = ItemManager.getItem(Name)
        ScenePlus = itemInManager.PlusScene
        if ScenePlus is not None:
            GroupZoom = GroupManager.getGroup(ScenePlus)
            Notification.notify(Notificator.onItemZoomEnter, GroupZoom, ScenePlus)
            return True
        # _________________________________________________________________________

        Notification.notify(Notificator.onInventoryPickInventoryItem, self)

        InventoryEntity = self.inventoryObject.getEntity()

        if ArrowManager.emptyArrowAttach() is True:
            InventoryEntity.pickInventoryItem(self.slotId)

        else:
            if self.item is None:
                return True

            InventoryEntity.combineInventoryItem(self.slotId)

        return True

    def getPoint(self):
        return self.point

    def setBlock(self, block):
        self.block = block

    def getBlock(self):
        return self.block

    def getHotSpot(self):
        return self.hotspot

    def getPointCameraPosition(self, Camera):
        return Mengine.getCameraPosition(Camera, self.point)

    def getItemOffset(self):
        itemEntity = self.item.getEntity()

        spriteCenter = itemEntity.getSpriteCenter()
        hotspotCenter = self.hotspot.getLocalPolygonCenter()

        x = hotspotCenter.x - spriteCenter[0]
        y = hotspotCenter.y - spriteCenter[1]

        return x, y

    def setItem(self, item):
        if self.hotspot is None:
            Trace.log("Entity", 0, "Inventory.setItem hotspot is None %s" % item.getName())
            return

        self.item = item
        self.item.setEnable(True)

        self.cursorItem = None

        itemEntity = self.item.getEntity()

        itemEntity.inInventory()
        itemPosition = self.getItemOffset()
        self.item.setPosition(itemPosition)

        itemEntityNode = self.item.getEntityNode()

        itemEntityNodeRender = itemEntityNode.getRender()
        itemEntityNodeRender.setLocalAlpha(1.0)

        InventoryItemScale = DefaultManager.getDefaultFloat("InventoryItemScale", 1.0)
        item.setScale((InventoryItemScale, InventoryItemScale, 1.0))

        self.point.addChild(itemEntityNode)
        self.hotspot.enable()

        self.hotspot.setEventListener(onHandleMouseEnter=self._onMouseEnter, onHandleMouseLeave=self._onMouseLeave, onHandleMouseOverDestroy=self._onHandleMouseOverDestroy, onHandleMouseButtonEvent=self._onMouseButtonEvent)

    def removeItem(self):
        self.hotspot.disable()

        if self.cursorItem is None and self.item is None:
            Trace.log("Inventory", 0, "InventorySlot removeItem is Empty")
            return

        removeItem = self.item or self.cursorItem

        self.item = None
        self.cursorItem = None

        removeItemEntity = removeItem.getEntity()
        removeItemEntity.removeFromParent()

        return removeItem

    def returnItem(self):
        self.hotspot.disable()

        if self.item is None:
            Trace.log("Inventory", 0, "InventorySlot removeItem is Empty")
            return

        self.cursorItem = self.item

        self.item = None

        removeItemEntity = self.cursorItem.getEntity()
        removeItemEntity.removeFromParent()

        return self.cursorItem

    def getItem(self):
        return self.item

    def getCursorItem(self):
        return self.cursorItem

    def empty(self):
        return self.item is None

    def getSlotID(self):
        return self.slotId

    def release(self):
        self.cursorItem = None

        if self.hotspot is not None:
            Mengine.destroyNode(self.hotspot)
            self.hotspot = None

        if self.item is not None:
            itemEntity = self.item.getEntity()
            itemEntity.removeFromParent()

            self.item = None

        if self.point is not None:
            Mengine.destroyNode(self.point)
            self.point = None

        self.inventoryObject = None

class Inventory(InventoryBase):
    @staticmethod
    def declareORM(Type):
        InventoryBase.declareORM(Type)

        Type.addAction(Type, "InventoryItems", Append=Inventory.__appendInventoryItems, Remove=Inventory.__removeInventoryItems)

        Type.addAction(Type, "SlotPoints")
        Type.addAction(Type, "SlotCount")
        Type.addActionActivate(Type, "CurrentSlotIndex", Update=Inventory._updateCurrentSlotIndex)

        Type.addAction(Type, "SlotPolygon")

        Type.addAction(Type, "BlockScrolling", Update=Inventory._updateItemReturn)

    def __init__(self):
        super(Inventory, self).__init__()

        self.slots = []

        self.onInventoryAttachInvItemToArrowObserver = None
        self.onAccountFinalizeObserver = None

        self.__detachItemTCs = {}

    def getSlots(self):
        return self.slots

    def __onAttachItemToArrow(self, invItem):
        slotID = self.object.getSlotID(invItem)
        self.pickInventoryItem(slotID)
        self.inventoryGlobalMouseEvent(True)
        return False

    def __onGlobalHandleMouseButtonEventEnd(self, event):
        def handleMouseButton_DefaultImplementation():
            if event.button != 0 or event.isDown is False:
                return

            if ArrowManager.emptyArrowAttach() is True:
                self.inventoryGlobalMouseEvent(False)
                return

            InventoryItem = ArrowManager.getArrowAttach()
            self.__detachInventoryItem(InventoryItem)

        def handleMouseButton_TouchpadImplementation():
            if event.button != 0 or event.isDown is True:
                return

            if ArrowManager.emptyArrowAttach() is True:
                self.inventoryGlobalMouseEvent(False)
                return

            InventoryItem = ArrowManager.getArrowAttach()

            if TaskManager.existTaskChain("InventoryMobileDetachItemTC") is True:
                return
            with TaskManager.createTaskChain(Name="InventoryMobileDetachItemTC") as tc:
                tc.addDelay(0.0)  # ensure that we will receive use on socket event before triggering invalid use
                tc.addFunction(self.__detachInventoryItem, InventoryItem)

        if Mengine.hasTouchpad() is True:
            # touchpad hot fix
            handleMouseButton_TouchpadImplementation()
        else:
            handleMouseButton_DefaultImplementation()

    def __detachInventoryItem(self, InventoryItem):
        def _DefaultImplementation():
            InventoryItemEntity = InventoryItem.getEntity()

            state = InventoryItemEntity.getState()

            PolicyPickInventoryItemEnd = PolicyManager.getPolicy("PickInventoryItemEnd", "PolicyPickInventoryItemEffectDummy")
            PolicyPickInventoryItemStop = PolicyManager.getPolicy("PickInventoryItemStop", "PolicyPickInventoryItemEffectDummy")

            tc_index = len(self.__detachItemTCs)
            tc = TaskManager.createTaskChain(Group=self.object, Cb=self.__cbUpdateInventoryOnDetach, CbArgs=(tc_index,))

            self.__detachItemTCs[tc_index] = tc

            Notification.notify(Notificator.onInventoryItemDetach, InventoryItem, state)

            with tc as tc:
                if state is InventoryItemEntity.ITEM_PICK:  # state 2
                    tc.addTask(PolicyPickInventoryItemEnd, InventoryItem=InventoryItem)
                    tc.addFunction(self.inventoryGlobalMouseEvent, False)
                    tc.addTask("AliasInventoryInvalidUseInventoryItem", Inventory=self.object)

                elif state is InventoryItemEntity.ITEM_RETURN:  # state 3
                    tc.addTask(PolicyPickInventoryItemEnd, InventoryItem=InventoryItem)
                    tc.addFunction(self.inventoryGlobalMouseEvent, False)
                    tc.addTask("AliasInventoryReturnInventoryItem", Inventory=self.object)

                elif state is InventoryItemEntity.ITEM_TAKE:  # state 5
                    tc.addTask(PolicyPickInventoryItemStop, InventoryItem=InventoryItem)
                    tc.addFunction(self.inventoryGlobalMouseEvent, False)
                    tc.addTask("AliasInventoryRemoveAttachInventoryItem", Inventory=self.object, InventoryItem=InventoryItem)

                elif state is InventoryItemEntity.ITEM_PLACE:  # state 4
                    with tc.addRaceTask(2) as (run, interrupt):
                        # fix when zoom opening removes effect
                        interrupt.addSemaphore(self.semaphoreOnZoomOpen, From=True, To=False)
                        run.addDelay(10)
                        run.addTask(PolicyPickInventoryItemStop, InventoryItem=InventoryItem)
                    tc.addFunction(InventoryItemEntity.pickAfterPlace)

                elif state is InventoryItemEntity.ITEM_TRY_COMBINE:
                    tc.addTask(PolicyPickInventoryItemEnd, InventoryItem=InventoryItem)
                    tc.addFunction(self.inventoryGlobalMouseEvent, False)
                    tc.addTask("AliasInventoryReturnInventoryItem", Inventory=self.object)

                elif state is InventoryItemEntity.ITEM_COMBINE:
                    tc.addTask(PolicyPickInventoryItemStop, InventoryItem=InventoryItem)
                    tc.addFunction(self.inventoryGlobalMouseEvent, False)

                else:
                    Trace.log("Entity", 0, "Inventory: unexpected error for detach {!r} state={}".format(InventoryItem.getName(), state))

        def _TouchpadImplementation():
            # changes affected AliasInventoryReturnInventoryItem and InventorySlot mouse handlers

            def __scopeReturnItem(source):
                source.addTask("AliasInventoryReturnInventoryItem", Inventory=self.object)
                source.addNotify(Notificator.onInventorySlotItemLeave, self.object, InventoryItem)

            def __scopeRemoveItem(source):
                source.addNotify(Notificator.onInventorySlotItemLeave, self.object, InventoryItem)
                source.addTask("AliasInventoryRemoveAttachInventoryItem", Inventory=self.object, InventoryItem=InventoryItem)

            InventoryItemEntity = InventoryItem.getEntity()

            state = InventoryItemEntity.getState()

            tc_index = len(self.__detachItemTCs)
            tc = TaskManager.createTaskChain(Group=self.object, Cb=self.__cbUpdateInventoryOnDetach, CbArgs=(tc_index,))

            self.__detachItemTCs[tc_index] = tc

            Notification.notify(Notificator.onInventoryItemDetach, InventoryItem, state)

            with tc as tc:
                if state is InventoryItemEntity.ITEM_PICK:  # state 2
                    tc.addFunction(self.inventoryGlobalMouseEvent, False)
                    tc.addScope(__scopeReturnItem)

                elif state is InventoryItemEntity.ITEM_RETURN:  # state 3
                    tc.addFunction(self.inventoryGlobalMouseEvent, False)
                    tc.addScope(__scopeReturnItem)

                elif state is InventoryItemEntity.ITEM_TAKE:  # state 5
                    tc.addFunction(self.inventoryGlobalMouseEvent, False)
                    tc.addScope(__scopeRemoveItem)

                elif state is InventoryItemEntity.ITEM_PLACE:  # state 4
                    tc.addFunction(InventoryItemEntity.pickAfterPlace)  # tc.addScope(__scopeReturnItem)

                elif state is InventoryItemEntity.ITEM_TRY_COMBINE:
                    tc.addFunction(self.inventoryGlobalMouseEvent, False)
                    tc.addScope(__scopeReturnItem)

                elif state is InventoryItemEntity.ITEM_COMBINE:
                    tc.addFunction(self.inventoryGlobalMouseEvent, False)
                else:
                    Trace.log("Entity", 0, "Inventory: unexpected error for detach {!r} state={}".format(InventoryItem.getName(), state))

        if Mengine.hasTouchpad() is True:
            _TouchpadImplementation()
        else:
            _DefaultImplementation()

    def __cbUpdateInventoryOnDetach(self, _isSkip, tc_index):
        self.__detachItemTCs.pop(tc_index)

        if len(self.__detachItemTCs) == 0:
            self._updateInventoryItem()
            self._updateButtonInteractive()

    def _updateInventoryItem(self):
        Notification.notify(Notificator.onInventoryUpdateItem)
        self.object.setParam("BlockScrolling", False)

    def _updateItemReturn(self, _value):
        Notification.notify(Notificator.onInventoryUpdateItem)

    def _updateCurrentSlotIndex(self, _CurrentSlotIndex):
        Notification.notify(Notificator.onInventoryCurrentSlotIndex, self.object)
        self._updateButtonInteractive()

    def inventoryGlobalMouseEvent(self, value):
        # fix for item drop
        if ArrowManager.emptyArrowAttach() is True and value is True:
            Mengine.enableGlobalHandler(self.MouseButtonHandlerID, False)
            return

        Mengine.enableGlobalHandler(self.MouseButtonHandlerID, value)

    def pickInventoryItem(self, slotId):
        def _DefaultImplementation():
            self.ButtonBlock()
            slot = self.slots[slotId]
            InventoryItem = slot.returnItem()

            ArrowManager.attachArrow(InventoryItem)

            InventoryItemEntity = InventoryItem.getEntity()
            InventoryItemEntity.pick()

            Notification.notify(Notificator.onInventoryItemPick, InventoryItem, InventoryItemEntity.getState())

            arrow = ArrowManager.getArrow()
            arrow.addChildFront(InventoryItemEntity.node)

            PickInventoryItem = PolicyManager.getPolicy("PickInventoryItem", "TaskEffectInventoryPickInventoryItem")
            TaskManager.runAlias(PickInventoryItem, None, InventoryItem=InventoryItem)

            with TaskManager.createTaskChain() as tc:
                tc.addTask("TaskMouseButtonClick")
                tc.addTask("TaskFunction", Fn=self.inventoryGlobalMouseEvent, Args=(True,))

        def _TouchpadImplementation():
            self.ButtonBlock()
            slot = self.slots[slotId]
            InventoryItem = slot.returnItem()

            ArrowManager.attachArrow(InventoryItem)

            InventoryItemEntity = InventoryItem.getEntity()
            InventoryItemEntity.pick()

            Notification.notify(Notificator.onInventoryItemPick, InventoryItem, InventoryItemEntity.getState())

            with TaskManager.createTaskChain() as tc:
                tc.addNotify(Notificator.onInventorySlotItemEnter, self.object, InventoryItem)
                tc.addTask("TaskMouseButtonClick", isDown=True)
                tc.addTask("TaskFunction", Fn=self.inventoryGlobalMouseEvent, Args=(True,))

        if Mengine.hasTouchpad() is True:
            _TouchpadImplementation()
        else:
            _DefaultImplementation()

    def combineInventoryItem(self, slotId):
        slot = self.slots[slotId]

        InventoryItem = ArrowManager.getArrowAttach()
        InventoryItemEntity = InventoryItem.getEntity()
        InventoryItemEntity.tryCombine()

        Notification.notify(Notificator.onInventoryCombineInventoryItem, self.object, InventoryItem, slot.item)

    def setupPoints(self):
        Sprite_InventoryPanel = self.object.getObject("Sprite_InventoryPanel")
        Sprite_InventoryPanelEntity = Sprite_InventoryPanel.getEntity()

        Position = Sprite_InventoryPanel.getPosition()
        Origin = Sprite_InventoryPanel.getOrigin()
        leftTop = (Position[0] - Origin[0], Position[1] - Origin[1])

        for index, point_position in enumerate(self.SlotPoints):
            point_node = Mengine.createNode("Point")

            hotspot_node = Mengine.createNode("HotSpotPolygon")
            hotspot_node.setPolygon(self.SlotPolygon)

            hotspot_node.disable()
            point_node.addChild(hotspot_node)

            delta = (point_position[0] - leftTop[0], point_position[1] - leftTop[1])
            point_node.setLocalPosition(delta)
            point_node.addChild(hotspot_node)
            Sprite_InventoryPanelEntity.addChild(point_node)

            slot = InventorySlot(self.object, index, point_node, hotspot_node)
            self.slots.append(slot)

    def _onPreparation(self):
        super(Inventory, self)._onPreparation()

        self.setupPoints()

    def _onActivate(self):
        super(Inventory, self)._onActivate()

        self.MouseButtonHandlerID = Mengine.addMouseButtonHandlerEnd(self.__onGlobalHandleMouseButtonEventEnd)
        Mengine.enableGlobalHandler(self.MouseButtonHandlerID, False)

        self.Socket_Inventory = self.object.getObject("Socket_Inventory")
        self.Socket_Inventory.setBlock(True)
        self.Socket_Inventory.setInteractive(True)

        self.updateSlots()

        self._updateButtonInteractive()

        # ===============================================================================
        # Interaction_InvRight
        with TaskManager.createTaskChain(Name="InventoryButtonInvRight", Group=self.object, Repeat=True) as tc:
            with tc.addRaceTask(2) as (tc_shift, tc_combine):
                with tc_shift.addRaceTask(2) as (source_shift_InvRight, source_shift_InvRightTemp):
                    source_shift_InvRight.addTask("TaskButtonClick", Group=self.object, ButtonName='Button_InvRight', AutoEnable=False)

                    source_shift_InvRightTemp.addTask("TaskButtonClick", Group=self.object, ButtonName='Button_InvRightTemp', AutoEnable=False)

                with tc_combine.addRaceTask(2) as (source_combine_InvRight, source_combine_InvRightTemp):
                    source_combine_InvRight.addTask("TaskButtonUse", Group=self.object, ButtonName='Button_InvRight', AutoEnable=False)

                    source_combine_InvRightTemp.addTask("TaskButtonUse", Group=self.object, ButtonName='Button_InvRightTemp', AutoEnable=False)

            tc.addTask("AliasInventorySlotsShiftRight", Inventory=self.object)
            tc.addTask("TaskNotify", ID=Notificator.onInventorySlotsShiftEnd)
            tc.addTask("TaskFunction", Fn=self._updateButtonInteractive)

        # ===============================================================================
        # Interaction_InvLeft
        with TaskManager.createTaskChain(Name="InventoryButtonInvLeft", Group=self.object, Repeat=True) as tc:
            with tc.addRaceTask(2) as (tc_shift, tc_combine):
                with tc_shift.addRaceTask(2) as (source_shift_InvLeft, source_shift_InvLeftTemp):
                    source_shift_InvLeft.addTask("TaskButtonClick", Group=self.object, ButtonName='Button_InvLeft', AutoEnable=False)

                    source_shift_InvLeftTemp.addTask("TaskButtonClick", Group=self.object, ButtonName='Button_InvLeftTemp', AutoEnable=False)

                with tc_combine.addRaceTask(2) as (source_combine_InvLeft, source_combine_InvLeftTemp):
                    source_combine_InvLeft.addTask("TaskButtonUse", Group=self.object, ButtonName='Button_InvLeft', AutoEnable=False)

                    source_combine_InvLeftTemp.addTask("TaskButtonUse", Group=self.object, ButtonName='Button_InvLeftTemp', AutoEnable=False)

            tc.addTask("AliasInventorySlotsShiftLeft", Inventory=self.object)
            tc.addTask("TaskNotify", ID=Notificator.onInventorySlotsShiftEnd)
            tc.addTask("TaskFunction", Fn=self._updateButtonInteractive)

        self.onInventoryAttachInvItemToArrowObserver = Notification.addObserver(Notificator.onInventoryAttachInvItemToArrow, self.__onAttachItemToArrow)
        self.onAccountFinalizeObserver = Notification.addObserver(Notificator.onAccountFinalize, self.__onAccountFinalize)

        Notification.notify(Notificator.onInventoryActivate, self.object)

        self.semaphoreOnZoomOpen = Semaphore(False, "InventoryOnZoomOpenSemaphore")
        with TaskManager.createTaskChain(Name="InventoryOnZoomOpenTC", Repeat=True) as tc:
            tc.addSemaphore(self.semaphoreOnZoomOpen, To=False)
            tc.addListener(Notificator.onZoomOpen, Filter=lambda value: value is not None)
            tc.addSemaphore(self.semaphoreOnZoomOpen, To=True)
            tc.addDelay(10)

    @staticmethod
    def __onAccountFinalize():
        Notification.notify(Notificator.onInventoryUpdateItem)

        return False

    def removeSlots(self):
        for slot in self.slots:
            slot.release()

        self.slots = []

    def _onDeactivate(self):
        super(Inventory, self)._onDeactivate()

        def __returnInvItemForce(_InventoryItem):
            PolicyPickInventoryItemStop = PolicyManager.getPolicy("PickInventoryItemStop", "PolicyPickInventoryItemEffectDummy")
            TaskManager.runAlias(PolicyPickInventoryItemStop, None, InventoryItem=_InventoryItem)
            TaskManager.runAlias("TaskInventorySlotReturnItem", None, InventoryItem=_InventoryItem, Inventory=self.object)
            TaskManager.runAlias("TaskObjectReturn", None, Object=_InventoryItem)

        if ArrowManager.emptyArrowAttach() is False:
            InventoryItem = ArrowManager.getArrowAttach()
            hasInventoryItem = self.object.hasInventoryItem(InventoryItem)
            if hasInventoryItem is True:
                __returnInvItemForce(InventoryItem)
                ArrowManager.removeArrowAttach()

        for slot in self.slots:
            slotCursorItem = slot.getCursorItem()
            if slotCursorItem is not None:
                __returnInvItemForce(slotCursorItem)

        self.removeSlots()

        Mengine.removeGlobalHandler(self.MouseButtonHandlerID)
        self.MouseButtonHandlerID = None

        self.Socket_Inventory.setBlock(False)
        self.Socket_Inventory.setInteractive(False)

        if TaskManager.existTaskChain("InventoryButtonInvRight") is True:
            TaskManager.cancelTaskChain("InventoryButtonInvRight")

        if TaskManager.existTaskChain("InventoryButtonInvLeft") is True:
            TaskManager.cancelTaskChain("InventoryButtonInvLeft")

        if TaskManager.existTaskChain("InventoryButtonInvRightWithItem") is True:
            TaskManager.cancelTaskChain("InventoryButtonInvRightWithItem")

        if TaskManager.existTaskChain("InventoryButtonInvLeftWithItem") is True:
            TaskManager.cancelTaskChain("InventoryButtonInvLeftWithItem")

        if TaskManager.existTaskChain("InventoryOnZoomOpenTC") is True:
            TaskManager.cancelTaskChain("InventoryOnZoomOpenTC")

        Notification.notify(Notificator.onInventoryDeactivate, self.object)

        Notification.removeObserver(self.onInventoryAttachInvItemToArrowObserver)
        Notification.removeObserver(self.onAccountFinalizeObserver)

        self.__detachItemTCs = {}

    def updateSlots(self):
        for InventoryItem in self.InventoryItems:
            InventoryItem.setEnable(False)

        activeSlot = self.object.getActiveSlots()

        for i in xrange(activeSlot):
            slot = self.slots[i]
            InventoryItem = self.InventoryItems[self.CurrentSlotIndex + i]

            slot.setItem(InventoryItem)

    def ButtonBlock(self):
        Button_InvLeft = self.object.getObject("Button_InvLeft")
        Button_InvRight = self.object.getObject("Button_InvRight")
        Button_InvLeftTemp = self.object.getObject("Button_InvLeftTemp")
        Button_InvRightTemp = self.object.getObject("Button_InvRightTemp")

        LeftInteractive = 0
        RightInteractive = 0

        Button_InvLeft.setParam("Interactive", LeftInteractive)
        Button_InvRight.setParam("Interactive", RightInteractive)
        Button_InvLeftTemp.setParam("Interactive", LeftInteractive)
        Button_InvRightTemp.setParam("Interactive", RightInteractive)

    def _updateButtonInteractive(self):
        Notification.notify(Notificator.onInventoryActionEnd)
        InventoryItemsCount = len(self.InventoryItems)

        self.object.getObject('Button_InvLeft').setEnable(False)
        self.object.getObject('Button_InvRight').setEnable(False)
        self.object.getObject('Button_InvLeftTemp').setEnable(False)
        self.object.getObject('Button_InvRightTemp').setEnable(False)

        self.Button_InvLeftName = 'Button_InvLeft'
        self.Button_InvRightName = 'Button_InvRight'

        last_slot_item = self.slots[-2].item if len(self.slots) >= 2 and self.slots[-2].item in self.InventoryItems else None
        first_slot_item = self.slots[0].item if len(self.slots) >= 1 and self.slots[0].item in self.InventoryItems else None

        if last_slot_item is not None and self.InventoryItems.index(last_slot_item) != InventoryItemsCount - 1:
            self.Button_InvRightName = 'Button_InvRightTemp'

        if first_slot_item is not None and self.InventoryItems.index(first_slot_item) != 0:
            self.Button_InvLeftName = 'Button_InvLeftTemp'

        Button_InvLeft = self.object.getObject(self.Button_InvLeftName)
        Button_InvRight = self.object.getObject(self.Button_InvRightName)

        InventoryLeftRightButtonHide = DefaultManager.getDefaultBool("InventoryLeftRightButtonHide", True)

        if InventoryLeftRightButtonHide is False:
            Button_InvLeft.setEnable(True)
            Button_InvRight.setEnable(True)

            Button_InvLeft.setParam("Interactive", 1)
            Button_InvRight.setParam("Interactive", 1)
            return

        Button_InvLeft.setEnable(False)
        Button_InvRight.setEnable(False)

        LeftInteractive = 0
        RightInteractive = 0

        if self.CurrentSlotIndex > 0:
            LeftInteractive = 1
            Button_InvLeft.setEnable(True)

        InventoryItemsCount = len(self.InventoryItems)

        if self.CurrentSlotIndex + self.SlotCount < InventoryItemsCount:
            RightInteractive = 1
            Button_InvRight.setEnable(True)

        Button_InvLeft.setParam("Interactive", LeftInteractive)
        Button_InvRight.setParam("Interactive", RightInteractive)

    def __checkEmptyCarriage(self):
        InventoryItems = self.object.getParam("InventoryItems")

        InventoryItemsCount = len(InventoryItems)

        if InventoryItemsCount <= self.CurrentSlotIndex:
            TaskManager.runAlias("AliasInventorySlotsShiftLeft", None, Inventory=self.object)

    def __appendInventoryItems(self, _id, inventoryItem):
        slot = self.findSlot(inventoryItem)

        Notification.notify(Notificator.onInventoryAppendInventoryItem, inventoryItem)

        if slot is None:
            return

        slot.setItem(inventoryItem)

    def __removeInventoryItems(self, _id, inventoryItem, _inventoryItems):
        self._updateButtonInteractive()
        self.__checkEmptyCarriage()

        slot = self.findSlot(inventoryItem)

        if slot is not None:
            slot.removeItem()

        Notification.notify(Notificator.onInventoryRemoveItem, inventoryItem)

    def findSlot(self, inventoryItem):
        for slot in self.slots:
            item = slot.getItem()
            if item is inventoryItem:
                return slot

            cursorItem = slot.getCursorItem()
            if cursorItem is inventoryItem:
                return slot