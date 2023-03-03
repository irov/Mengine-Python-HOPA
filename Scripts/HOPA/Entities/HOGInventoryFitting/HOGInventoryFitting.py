from Foundation.ArrowManager import ArrowManager
from Foundation.TaskManager import TaskManager
from HOPA.Entities.InventoryBase import InventoryBase
from HOPA.HOGFittingItemManager import HOGFittingItemManager
from Notification import Notification


InventoryBase = Mengine.importEntity("InventoryBase")

ALPHA_TIME = 200.0
TC_ZOOM_ALPHA_NAME = "HOGFittingZoomAlpha"


class InventoryFittingSlot(object):
    def __init__(self, slotID, SocketName, hotspot, MovieSlot, inventoryObject):
        self.slotID = slotID
        self.SocketName = SocketName
        self.SocketHotSpot = hotspot

        self.MovieSlot = MovieSlot

        self.ItemName = None
        self.SlotIsFitting = True

        self.ItemScene = None
        self.ItemStore = None
        self.ItemHideStore = None
        self.ItemZoomStore = None

        self.inventoryObject = inventoryObject
        self.pick = False
        self.EnableSocket()

        pass

    def _onMouseEnter(self, x, y):
        if self.ItemName is None:
            return False
        if Mengine.hasTouchpad() is True:
            return True  # If player set cursor via touchpad over item - it will play effects - we need to block it

        if self.SlotIsFitting is False:
            Notification.notify(Notificator.onInventoryItemMouseEnter, self.ItemStore)
        Notification.notify(Notificator.onInventorySlotItemEnter, self.inventoryObject, self.ItemHideStore)

        return True

    def _onMouseLeave(self):
        if self.ItemName is None:
            return
        if Mengine.hasTouchpad() is True:
            return True  # If player set cursor via touchpad over item - it will play effects - we need to block it

        if self.SlotIsFitting is False:
            Notification.notify(Notificator.onInventoryItemMouseLeave, self.ItemStore)
        Notification.notify(Notificator.onInventorySlotItemLeave, self.inventoryObject, self.ItemHideStore)

    def getItemOffset(self, item):
        itemEntity = item.getEntity()

        itemSlotPoint = item.getSlotPoint()
        if itemSlotPoint is None:
            itemSlotPoint = itemEntity.getSpriteCenter()
            pass

        x = (-itemSlotPoint[0])
        y = (-itemSlotPoint[1])

        return (x, y)

    def prepareSlot(self, ItemName):
        if ItemName is None:
            return
            pass

        self.setPick(False)

        self.setFitting(True)

        self.ItemName = ItemName
        Item = HOGFittingItemManager.getItem(self.ItemName)

        self.ItemScene = Item.SceneObject
        self.ItemStore = Item.StoreObject
        self.ItemHideStore = Item.StoreHideObject
        self.ItemZoomStore = Item.StoreZoomObject

        pos = self.getItemOffset(self.ItemStore)
        self.ItemStore.setPosition(pos)
        self.ItemStore.setEnable(False)
        pos = self.getItemOffset(self.ItemHideStore)
        self.ItemHideStore.setPosition(pos)

        self.ItemStore.setScale((1, 1, 1))

        EntityItemStoreNode = self.ItemStore.getEntityNode()
        EntityItemHideStoreNode = self.ItemHideStore.getEntityNode()

        self.MovieSlot.addChild(EntityItemStoreNode)
        self.MovieSlot.addChild(EntityItemHideStoreNode)
        pass

    def ClearSlot(self):
        if (self.ItemName is not None):
            self.MovieSlot.removeChildren()
            pass

        self.ItemName = None
        self.SlotIsFitting = True

        self.ItemScene = None
        self.ItemStore = None
        self.ItemHideStore = None

        self.DisableSocket()
        pass

    def setFitting(self, fitting):
        self.EnableSocket()
        if (self.ItemName is None):
            return
        self.SlotIsFitting = fitting
        if self.SlotIsFitting is True:
            self.ItemHideStore.setEnable(True)
            self.ItemStore.setEnable(False)
            pass
        else:
            self.ItemHideStore.setEnable(False)
            self.ItemStore.setEnable(True)
            pass
        pass

    def setPick(self, value):
        self.pick = value
        pass

    def PickItem(self):
        self.DisableSocket()
        self.setPick(True)
        self.ItemHideStore.setEnable(True)
        pass

    def ReturnItem(self):
        if self.SlotIsFitting is True:
            self.ItemHideStore.setEnable(True)
            EntityItemStoreNode = self.ItemHideStore.getEntityNode()
            self.MovieSlot.addChild(EntityItemStoreNode)
            pos = self.getItemOffset(self.ItemHideStore)
            self.ItemHideStore.setPosition(pos)
            self.ItemHideStore.setScale((1, 1, 1))
            return
            pass
        EntityItemStoreNode = self.ItemStore.getEntityNode()
        self.MovieSlot.addChild(EntityItemStoreNode)
        self.ItemHideStore.setEnable(False)
        self.ItemStore.setEnable(True)

        pos = self.getItemOffset(self.ItemStore)
        self.ItemStore.setPosition(pos)
        pos = self.getItemOffset(self.ItemHideStore)
        self.ItemHideStore.setPosition(pos)
        self.ItemHideStore.setScale((1, 1, 1))
        self.ItemStore.setScale((1, 1, 1))
        self.setPick(False)
        self.EnableSocket()
        pass

    def EnableSocket(self):
        self.SocketHotSpot.enable()
        self.SocketHotSpot.setEventListener(onHandleMouseEnter=self._onMouseEnter,
                                            onHandleMouseLeave=self._onMouseLeave)

    def DisableSocket(self):
        self.SocketHotSpot.disable()
        self.SocketHotSpot.setEventListener(onHandleMouseEnter=None, onHandleMouseLeave=None)

    def getPoint(self):
        return self.MovieSlot.getWorldPosition()


class HOGInventoryFitting(InventoryBase):

    @staticmethod
    def declareORM(Type):
        InventoryBase.declareORM(Type)
        Type.addAction(Type, "SlotCount")
        Type.addAction(Type, "SlotItems")
        Type.addAction(Type, "SlotIsFitting")
        Type.addActionActivate(Type, "SlotFittingItemList",
                               Append=HOGInventoryFitting._AppendSlotFittingItemList,
                               Update=HOGInventoryFitting._updateSlotFittingItemList)
        Type.addActionActivate(Type, "ItemList",
                               Append=HOGInventoryFitting._AppendItemList,
                               Update=HOGInventoryFitting._updateItemList)
        Type.addActionActivate(Type, "SlotFittingItemListUsed",
                               Append=HOGInventoryFitting._AppendSlotFittingItemListUsed,
                               Update=HOGInventoryFitting._updateSlotFittingItemListUsed)
        pass

    def __init__(self):
        super(HOGInventoryFitting, self).__init__()
        self.slots = []
        self.Movie = None
        self.ItemIsPicked = False
        self.PickedItemSlot = None
        self.ItemIsValideUse = False
        self.SlotCountIn = 0

        self.__secondClick = False  # for touchpad Click&Click

        self.CurrentItemZoomStore = None
        self.CurrentItemStore = None
        pass

    def _onInitialize(self, obj):
        super(HOGInventoryFitting, self)._onInitialize(obj)
        pass

    def _onPreparation(self):
        super(HOGInventoryFitting, self)._onPreparation()
        self.__Init()

    def _onDeactivate(self):
        super(HOGInventoryFitting, self)._onDeactivate()
        self.__End()

        if TaskManager.existTaskChain(TC_ZOOM_ALPHA_NAME):
            TaskManager.cancelTaskChain(TC_ZOOM_ALPHA_NAME)

        pass

    def __Init(self):
        self.SlotCountIn = self.SlotCount
        self.Socket_Inventory = self.object.getObject("Socket_Inventory")
        self.Socket_Inventory.setInteractive(True)
        self.Socket_Inventory.setBlock(True)

        self.__InitSlots()

        for i in range(self.SlotCountIn):
            self.__InitSlotAlias(i)
            pass

        self.MouseButtonHandlerID = Mengine.addMouseButtonHandlerEnd(self._onGlobalHandleMouseButtonEventEnd)
        self.__InitReturnAlias()
        pass

    def __End(self):
        for i in range(self.SlotCountIn):
            if TaskManager.existTaskChain("HOGSlotAction_%d" % (i)) is True:
                TaskManager.cancelTaskChain("HOGSlotAction_%d" % (i))
                pass
            pass

        if TaskManager.existTaskChain("HOGFittingReturnAlias") is True:
            TaskManager.cancelTaskChain("HOGFittingReturnAlias")
            pass

        Mengine.removeGlobalHandler(self.MouseButtonHandlerID)
        self.MouseButtonHandlerID = None

        self._removeItemAttach()

        for slot in self.slots:
            slot.ClearSlot()

        self.slots = []
        self.Movie = None
        self.ItemIsPicked = False
        self.PickedItemSlot = None
        self.ItemIsValideUse = False
        pass

    def _AppendSlotFittingItemList(self, id, ItemName):
        self.PrepareSlotForItem(ItemName)
        pass

    def _updateSlotFittingItemList(self, list):
        for name in list:
            self.PrepareSlotForItem(name)
            pass
        pass

    def _AppendItemList(self, id, ItemName):
        self.AddItemOriginToSlot(ItemName)
        slot = self.getSlotByName(ItemName)
        slot.setFitting(False)
        slot.ReturnItem()
        pass

    def _updateItemList(self, list):
        for name in list:
            self.AddItemOriginToSlot(name)
            slot = self.getSlotByName(name)
            slot.setFitting(False)
            pass
        pass

    def _AppendSlotFittingItemListUsed(self, id, ItemName):
        self.removeSlotItem(ItemName)
        self.ItemIsValideUse = False
        pass

    def _removeItemAttach(self):
        if ArrowManager.emptyArrowAttach() is True:
            return

        attach = ArrowManager.getArrowAttach()
        if Mengine.hasTouchpad() is True:
            Notification.notify(Notificator.onInventorySlotItemLeave, self.object, attach)
            slot = self.PickedItemSlot
            self.returnSlotItem(slot.ItemName)
        else:
            itemEntity = attach.getEntity()
            itemEntity.removeFromParent()
        ArrowManager.removeArrowAttach()

        Notification.notify(Notificator.onHOGFittingItemDetached, attach)

    def _updateSlotFittingItemListUsed(self, list):
        for name in list:
            self.removeSlotItem(name)
            pass
        self.ItemIsValideUse = False
        pass

    def __InitSlots(self):
        self.Movie = self.object.getObject("Movie2_SlotPoints")
        for id in range(self.SlotCountIn):
            SocketName = "socket_%d" % (id)
            MovieSlot = self.__getMovieSlot(id)
            hotspot = self.__getHotSpot(SocketName)
            slot = InventoryFittingSlot(id, SocketName, hotspot, MovieSlot, self.object)
            self.slots.append(slot)
            pass

        SlotItems = self.object.getSlotItems()
        if len(SlotItems) == 0:
            for id in range(self.SlotCountIn):
                self.object.appendParam("SlotItems", None)
                self.object.appendParam("SlotIsFitting", True)
                pass
            pass
        else:
            itemNames = self.object.getSlotItems()
            itemFittings = self.object.getSlotIsFitting()
            for i in range(self.SlotCountIn):
                slot = self.slots[i]
                itemName = itemNames[i]
                itemFitting = itemFittings[i]

                slot.prepareSlot(itemName)
                slot.setFitting(itemFitting)
                pass
            pass
        pass

    def __InitSlotAlias(self, id):
        slot = self.slots[id]

        with TaskManager.createTaskChain(Name="HOGSlotAction_%d" % (id), Repeat=True) as tc:
            if Mengine.hasTouchpad():
                # touchpad hot fix
                tc.addTask("TaskMovie2SocketClick", isDown=True, SocketName=slot.SocketName, Movie2=self.Movie)
            else:
                tc.addTask("TaskMovie2SocketClick", SocketName=slot.SocketName, Movie2=self.Movie)

            tc.addFunction(self.ItemPick, id)

    def ItemPick(self, slot_id):
        slot = self.slots[slot_id]

        if ArrowManager.emptyArrowAttach() is False:
            self._removeItemAttach()
        if slot.SlotIsFitting is True:
            return

        def _DragAndDrop():  # PC version
            Notification.notify(Notificator.onInventoryPickInventoryItem, slot.ItemHideStore)

            Mengine.enableGlobalHandler(self.MouseButtonHandlerID, True)

            slot.ItemHideStore.setEnable(True)
            slot.PickItem()
            Item = slot.ItemStore
            ArrowManager.attachArrow(Item)
            arrow = ArrowManager.getArrow()
            ItemEntityNode = Item.getEntityNode()
            arrow.addChildFront(ItemEntityNode)
            self.ItemIsPicked = True
            self.PickedItemSlot = slot

            Notification.notify(Notificator.onHOGFittingItemPicked, Item.name)
            self.__currentItemZoomShow()

        def _ClickAndClick():  # Touchpad version
            Item = slot.ItemStore

            Notification.notify(Notificator.onInventoryPickInventoryItem, slot.ItemHideStore)
            Notification.notify(Notificator.onInventorySlotItemEnter, self.object, Item)

            slot.DisableSocket()
            slot.setPick(True)

            ArrowManager.attachArrow(Item)
            self.ItemIsPicked = True
            self.PickedItemSlot = slot

            Notification.notify(Notificator.onHOGFittingItemPicked, Item.name)

        if Mengine.hasTouchpad() is True:
            _ClickAndClick()
        else:
            _DragAndDrop()

    def __InitReturnAlias(self):
        with TaskManager.createTaskChain(Name="HOGFittingReturnAlias", Repeat=True) as tc:
            tc.addTask("TaskListener", ID=Notificator.onHOGFittinItemReturn)
            tc.addFunction(self.__currentItemZoomHide)
            tc.addTask("AliasHOGFittingReturnItemToSlot", Inventory=self.object)
            pass
        pass

    def _onGlobalHandleMouseButtonEventEnd(self, event):
        def handleMouseButton_DefaultImplementation():
            if event.button != 0 or event.isDown is False:
                return
                pass

            if ArrowManager.emptyArrowAttach() is True:
                return
                pass

            if self.ItemIsPicked is False:
                return
                pass

            if self.ItemIsValideUse is True:
                self.ItemIsValideUse = False
                return
                pass

            attach = ArrowManager.getArrowAttach()

            for id, slot in enumerate(self.slots):
                if slot.ItemStore is attach:
                    Notification.notify(Notificator.onHOGFittinItemReturn)
                    return
                    pass
                pass

            for itemName in self.SlotFittingItemListUsed:
                if itemName is attach.getName():
                    self._removeItemAttach()
                    pass
                pass
            pass

        def handleMouseButton_TouchpadImplementation():  # Click&Click
            if event.button != 0 or event.isDown is True:
                return

            if ArrowManager.emptyArrowAttach() is True:
                return

            if self.ItemIsPicked is False:
                return

            if self.ItemIsValideUse is True:
                self.ItemIsValideUse = False
                return

            if self.__secondClick is False:
                self.__secondClick = True
                return
            self.__secondClick = False

            attach = ArrowManager.getArrowAttach()

            if TaskManager.existTaskChain("HOGInventoryFittingMobileTC") is True:
                return
            with TaskManager.createTaskChain(Name="HOGInventoryFittingMobileTC") as tc:
                tc.addDelay(0.0)  # ensure that we will receive use on socket event before triggering invalid use

                for id, slot in enumerate(self.slots):
                    if slot.ItemStore is attach:
                        tc.addFunction(self._removeItemAttach)
                        return

                for itemName in self.SlotFittingItemListUsed:
                    if itemName is attach.getName():
                        tc.addFunction(self._removeItemAttach)

        if Mengine.hasTouchpad():
            # touchpad hot fix
            handleMouseButton_TouchpadImplementation()
        else:
            handleMouseButton_DefaultImplementation()

    def __getMovieSlot(self, slotID):
        MovieSlotPointsEntity = self.Movie.getEntity()
        id = "slot_%d" % (slotID)
        CurrentSlot = MovieSlotPointsEntity.getMovieSlot(id)
        return CurrentSlot
        pass

    def __getHotSpot(self, SocketName):
        MovieSlotPointsEntity = self.Movie.getEntity()
        hotspot = MovieSlotPointsEntity.getSocket(SocketName)
        return hotspot
        pass

    def PrepareSlotForItem(self, ItemName):
        for id, slot in enumerate(self.slots):
            if slot.ItemName is None:
                slot.prepareSlot(ItemName)
                self.object.changeParam("SlotItems", id, ItemName)
                return slot
                pass
            pass

        Trace.log("Entity", 0, "Can't find free slot for item with name %s" % ItemName)
        return None
        pass

    def AddItemOriginToSlot(self, ItemName):
        for id, slot in enumerate(self.slots):
            if slot.ItemName == ItemName:
                self.object.changeParam("SlotIsFitting", id, False)
                return
            pass

        Trace.log("Entity", 0, "Can't find prepare slot for item with name %s" % ItemName)
        pass

    def removeSlotItem(self, ItemName):
        self.__currentItemZoomHide(True)
        self._removeItemAttach()

        Notification.notify(Notificator.onHOGFittingItemUsed, ItemName)

        for id, slot in enumerate(self.slots):
            if slot.ItemName == ItemName:
                slot.ClearSlot()
                self.object.changeParam("SlotItems", id, None)
                self.object.changeParam("SlotIsFitting", id, True)
                return
            pass

        Trace.log("Entity", 0, "Can't find slot with name %s" % ItemName)
        pass

    def returnSlotItem(self, ItemName):
        slot = self.getSlotByName(ItemName)
        slot.ReturnItem()
        # self._removeItemAttach()
        pass

    def DisableSlotItem(self, ItemName):
        self._removeItemAttach()
        slot = self.getSlotByName(ItemName)
        slot.DisableSocket()
        self._removeItemAttach()
        pass

    def getSlotByName(self, ItemName):
        for slot in self.slots:
            if slot.ItemName == ItemName:
                return slot
                pass
            pass

        Trace.log("Entity", 0, "Can't getSlotByName with name %s" % ItemName)
        return None
        pass

    def ItemInSlot(self, ItemObj):
        for slot in self.slots:
            if (slot.ItemStore == ItemObj and slot.SlotIsFitting is False):
                return True
            pass
        return False
        pass

    pass

    def hasFreeSlot(self):
        if len(self.slots) == 0:
            # Trace.log("Entity", 0, "HOGInventoryFitting.hasFreeSlot(): you need init your slots first!")
            return False

        slots = [slot.ItemName for slot in self.slots]

        return None in slots

    def __currentItemZoomHide(self, instant=False):
        if self.CurrentItemZoomStore is None or not self.CurrentItemZoomStore.isActive():
            return

        CurrentItemZoomStore = self.CurrentItemZoomStore
        self.CurrentItemZoomStore = None

        CurrentItemStore = self.CurrentItemStore
        self.CurrentItemStore = None

        CurrentItemStore.setEnable(True)

        def zoomHide(*_):
            CurrentItemZoomStore.setEnable(False)
            CurrentItemZoomStore.returnToParent()
            CurrentItemStore.setAlpha(1.0)

        if instant:
            zoomHide()

        else:
            if TaskManager.existTaskChain(TC_ZOOM_ALPHA_NAME):
                TaskManager.cancelTaskChain(TC_ZOOM_ALPHA_NAME)

            with TaskManager.createTaskChain(Name=TC_ZOOM_ALPHA_NAME, Cb=zoomHide) as tc:
                with tc.addParallelTask(2) as (parallel_1, parallel_2):
                    parallel_1.addTask("TaskNodeAlphaTo", Node=CurrentItemZoomStore.entity.node, To=0.0, Time=ALPHA_TIME)
                    parallel_2.addTask("TaskNodeAlphaTo", Node=CurrentItemStore.getEntityNode(), To=1.0, Time=ALPHA_TIME)

    def __currentItemZoomShow(self):
        self.CurrentItemZoomStore = self.PickedItemSlot.ItemZoomStore
        self.CurrentItemStore = self.PickedItemSlot.ItemStore

        if self.CurrentItemZoomStore is None or not self.CurrentItemZoomStore.isActive():
            return

        self.CurrentItemZoomStore.setAlpha(0.0)
        self.CurrentItemZoomStore.setEnable(True)

        node = self.CurrentItemZoomStore.entity.node
        Mengine.getArrow().addChild(node)

        offset_vec2 = self.CurrentItemZoomStore.entity.sprite.getSurfaceSize()
        node.setWorldPosition(
            Mengine.getArrow().node.getWorldPosition() - (offset_vec2.x * 0.5, offset_vec2.y * 0.5, 0.0))

        if TaskManager.existTaskChain(TC_ZOOM_ALPHA_NAME):
            TaskManager.cancelTaskChain(TC_ZOOM_ALPHA_NAME)

        with TaskManager.createTaskChain(Name=TC_ZOOM_ALPHA_NAME) as tc:
            with tc.addParallelTask(2) as (parallel_1, parallel_2):
                parallel_1.addTask("TaskNodeAlphaTo", Node=self.CurrentItemZoomStore.getEntityNode(),
                                   To=1.0, Time=ALPHA_TIME)
                parallel_2.addTask("TaskNodeAlphaTo", Node=self.CurrentItemStore.getEntityNode(),
                                   To=0.0, Time=ALPHA_TIME)
