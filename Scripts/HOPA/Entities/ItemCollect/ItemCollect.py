from Foundation.DefaultManager import DefaultManager
from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.GuardBlockInput import GuardBlockInput
from Foundation.Notificator import Notificator
from Foundation.SceneManager import SceneManager
from Foundation.TaskManager import TaskManager
from HOPA.System.SystemItemCollect import SystemItemCollect
from Holder import Holder
from Notification import Notification


class ItemCollect(BaseEntity):
    s_openingProcessProgress = False

    @staticmethod
    def setOpeningProcessProgress(flag):
        ItemCollect.s_openingProcessProgress = flag

    @staticmethod
    def getOpeningProcessProgress():
        return ItemCollect.s_openingProcessProgress

    class Slot(object):
        def __init__(self, id_, movie, icon):
            self.ID = id_
            self.Movie = movie
            self.Node = movie.getEntityNode()
            self.Icon = icon
            self.state = icon.Idle.getEnable()
            self.allowedMovies = dict()  # allowed circles

        def enableIcon(self, flag):
            self.Icon.switchIcon(flag)
            self.state = flag

        def getSocket(self):
            return self.Movie.getSocket('socket')

    @staticmethod
    def declareORM(Type):
        BaseEntity.declareORM(Type)
        Type.addAction(Type, 'ItemCollectArea')
        Type.addAction(Type, 'ItemsList')
        Type.addAction(Type, 'Radius')
        Type.addAction(Type, 'DeviationAngle')
        Type.addAction(Type, 'AttachItem')
        Type.addAction(Type, 'PreAttach')

    def __init__(self):
        super(ItemCollect, self).__init__()
        self.tc = None
        self.tc_select_effect = None
        self.itemSlots = {}
        self.attachItemToCursor = None
        self.attachItemToCursor_Cash = None
        self._root = None

    def _onPreparation(self):
        super(ItemCollect, self)._onPreparation()
        Notification.notify(Notificator.onClickItemCollectHintSocket)

    def _onActivate(self):
        super(ItemCollect, self)._onActivate()
        with TaskManager.createTaskChain() as tc:
            tc.addFunction(self.createRootNode)
            tc.addScope(self.playSceneEffect_Inst, True)
            tc.addFunction(self.setItemsSlots)
            tc.addScope(self.playSceneEffect_Inst, False)
            tc.addScope(self.playSceneEffect, True)
            tc.addFunction(self._runTaskChain)

    def _onDeactivate(self):
        super(ItemCollect, self)._onDeactivate()
        self._cleanUp()

    def createRootNode(self):
        scene = SceneManager.getCurrentScene()
        layer = scene.getMainLayer()
        position = self.node.getWorldPosition()

        node = Mengine.createNode("Interender")
        node.setName("ItemCollectRoot")
        node.setLocalPosition(position)
        layer.addChild(node)

        self._root = node

    def setItemsSlots(self):
        ItemsList = self.object.getParam('ItemsList')
        radius = self.object.getParam('Radius')

        for ItemName in ItemsList:
            itemMovie = self.object.tryGenerateObjectUnique('SmallCircle_{}'.format(ItemName), "Movie2_SmallCircle", Enable=True)
            Icon = SystemItemCollect.getItemCollect(ItemName)
            itemPlace = ItemCollect.Slot(ItemName, itemMovie, Icon)

            self._root.addChild(itemPlace.Node)
            itemPlace.Node.setLocalPosition((0.0, -radius, 0.0))

            itemPlace.Node.addChild(Icon.Idle.getEntityNode())
            itemPlace.Node.addChild(Icon.Silhouette.getEntityNode())

            iconIdleSpriteCenter = self.getSpriteCenter(Icon.Idle)
            iconSilhouetteSpriteCenter = self.getSpriteCenter(Icon.Silhouette)

            icon_idle_pos = Mengine.vec2f(-iconIdleSpriteCenter[0], -iconIdleSpriteCenter[1])
            icon_silhouette_pos = Mengine.vec2f(-iconSilhouetteSpriteCenter[0], -iconSilhouetteSpriteCenter[1])

            Icon.Idle.getEntityNode().setLocalPosition(icon_idle_pos)
            Icon.Silhouette.getEntityNode().setLocalPosition(icon_silhouette_pos)

            if SystemItemCollect.hasFoundItem(ItemName):
                itemPlace.enableIcon(True)
            else:
                itemPlace.enableIcon(False)

            self.itemSlots[ItemName] = itemPlace

        for itemName, itemSlot in self.itemSlots.items():
            for AllowedItemName in itemSlot.Icon.AllowedItems:
                itemSlot_ = self.itemSlots.get(AllowedItemName)
                if itemSlot_ is not None:
                    itemSlot.allowedMovies[AllowedItemName] = itemSlot_.Movie
            itemSlot.allowedMovies[itemName] = itemSlot.Movie  # add own movie too

        self.setSlots()

    def setSlots(self):
        ItemsList = self.object.getParam('ItemsList')
        evenFlag = True
        disp = int(self.object.getParam('DeviationAngle'))
        if len(ItemsList) % 2 != 0:
            evenFlag = False
        angle = 0
        for i, slot in enumerate(self.itemSlots.values()):
            if i == 0:
                if evenFlag is True:
                    angle = disp / 2
                    angle *= -1
            else:
                if angle > 0:
                    angle += disp
                    angle *= -1
                elif angle < 0:
                    angle -= 2 * angle
                else:
                    angle += disp
                    angle *= -1

            startPosition = slot.Node.getLocalPosition()
            position = self.calcSlotPosition(angle, startPosition)
            slot.Node.setLocalPosition(position)

            if slot.Icon.ItemPosition is None:
                slot.Icon.ItemPosition = slot.Node.getWorldPosition()

    @staticmethod
    def calcSlotPosition(angle, startPosition):
        # center at (0.0, 0.0)
        rx = startPosition.x
        ry = startPosition.y
        c = Mengine.cosf_deg(angle)
        s = Mengine.sinf_deg(angle)
        x1 = rx * c - ry * s
        y1 = rx * s + ry * c
        return Mengine.vec2f(x1, y1)

    @staticmethod
    def getSpriteCenter(sprite):
        spriteEntity = sprite.getEntity()
        imageSize = spriteEntity.getSize()
        imageCenter = (imageSize.x * 0.5, imageSize.y * 0.5)
        return imageCenter

    @staticmethod
    def _setScale(node, to):
        node.setScale(to)

    @staticmethod
    def _setRotate(node, to):
        node.setAngle(to)

    def playSceneEffect_Inst(self, source, flag):
        node = self._root
        ScaleTo = (1.0, 1.0, 1.0) if flag is True else (0.0, 0.0, 0.0)
        RotateTo = 6.28319 if flag is True else 3.14
        with GuardBlockInput(source) as guard_source:
            with guard_source.addParallelTask(2) as (p1, p2):
                p1.addFunction(self._setScale, node, ScaleTo)
                p1.addFunction(self._setRotate, node, RotateTo)

    def playSceneEffect(self, source, flag):
        if self._root is None:
            Trace.log("Entity", 0, "ItemCollect.playSceneEffect: _root is None (entity activate is {})".format(self.isActivate()))
            return

        node = self._root
        ScaleTo = (1.0, 1.0, 1.0) if flag is True else (0.0, 0.0, 0.0)
        ScaleFrom = (0.0, 0.0, 0.0) if flag is True else (1.0, 1.0, 1.0)
        AlphaTo = 1.0 if flag is True else 0.0
        AlphaFrom = 0.0 if flag is True else 1.0
        RotateTo = 6.28319 if flag is True else 3.14
        RotateFrom = 3.14 if flag is True else 6.28319
        Time = DefaultManager.getDefaultInt('OpenAndCloseItemCollectTime', 1000)

        with GuardBlockInput(source) as guard_source:
            guard_source.addFunction(ItemCollect.setOpeningProcessProgress, True)
            with guard_source.addParallelTask(4) as (p1, p2, p3, p_Sound):
                if flag is True:
                    p_Sound.addNotify(Notificator.onSoundEffectOnObject, self.object, 'ItemCollect_Open')
                else:
                    if self.attachItemToCursor_Cash is not None:
                        p_Sound.addTask("AliasRemoveItemAttach", Item=self.attachItemToCursor_Cash)
                    p_Sound.addNotify(Notificator.onSoundEffectOnObject, self.object, 'ItemCollect_Close')
                p1.addTask('TaskNodeAlphaTo', Node=node, To=AlphaTo, From=AlphaFrom, Time=Time)
                p2.addTask('TaskNodeRotateTo', Node=node, To=RotateTo, From=RotateFrom, Time=Time)
                p3.addTask('TaskNodeScaleTo', Node=node, From=ScaleFrom, To=ScaleTo, Time=Time)
                guard_source.addFunction(ItemCollect.setOpeningProcessProgress, False)

    def __onEnigmaSkip(self):
        for slot in self.itemSlots.values():
            slot.enableIcon(True)
            Notification.notify(Notificator.onItemCollectSetItem, slot.Icon.Item)
            SystemItemCollect.addFoundItem(slot.ID)
            Notification.notify(Notificator.onHintActionItemCollectEnd)
        Notification.notify(Notificator.onFinishItemCollect, Mengine.getCurrentScene().getName(), self.ItemCollectArea, True)
        return False

    def _runTaskChain(self):
        self.tc = TaskManager.createTaskChain(Repeat=True)
        with self.tc as tc:
            with tc.addRaceTask(2) as (source, skip):
                source.addScope(self._clickOnItem)
                with source.addIfTask(self.checkComplete) as (true, false):
                    true.addNotify(Notificator.onFinishItemCollect, Mengine.getCurrentScene().getName(), self.ItemCollectArea, True)

                skip.addListener(Notificator.onEnigmaSkip, Filter=self.__onEnigmaSkip)

    def stopItemSelectEffect(self):
        if self.tc_select_effect is not None:
            self.tc_select_effect.cancel()
            self.tc_select_effect = None

    def playItemSelectEffect(self, itemObject):
        if Mengine.hasTouchpad() is False:
            return

        if self.tc_select_effect is not None:
            return

        # params
        ScaleTo = 1.1
        ScaleTime = 250.0

        itemNode = itemObject.getEntityNode()

        def _cbStop(isSkip, node):
            node.scaleStop()
            node.setScale((1.0, 1.0, 1.0))
            self.tc_select_effect = None

        self.tc_select_effect = TaskManager.createTaskChain(
            Name="ItemCollectSelectEffect_{}".format(itemObject.getName()), Cb=_cbStop, CbArgs=(itemNode,), Repeat=True)
        with self.tc_select_effect as tc:
            tc.addTask("TaskNodeScaleTo", Node=itemNode, To=(ScaleTo, ScaleTo, 1.0), Time=ScaleTime)
            tc.addTask("TaskNodeScaleTo", Node=itemNode, To=(1.0, 1.0, 1.0), Time=ScaleTime)

    def _clickOnItem(self, source):
        ClickHolder = Holder()
        if self.PreAttach is not None:
            source.addTask("AliasRemoveItemAttach", Item=self.PreAttach)
            self.object.setPreAttach(None)

        OffsetValue = DefaultManager.getDefaultTuple("ItemCollectAttachOffset", (0, 0), valueType=int, divider=", ")
        if self.AttachItem is None or self.AttachItem == '':
            for (itemName, Slot), race in source.addRaceTaskList(self.itemSlots.iteritems()):
                hotspot = Slot.Icon.Item.entity.getHotSpot()
                race.addTask('AliasItemAttach', Item=Slot.Icon.Item,
                             OffsetValue=OffsetValue, AddArrowChild=Mengine.hasTouchpad() is False)
                race.addFunction(hotspot.disable)
                race.addFunction(ClickHolder.set, Slot)
                race.addNotify(Notificator.onSoundEffectOnObject, self.object, 'ItemCollect_Pick')
        else:
            Item = self.itemSlots[self.AttachItem].Icon.Item
            hotspot = Item.entity.getHotSpot()
            source.addTask("TaskFanItemInHand", FanItem=Item)
            source.addTask("TaskArrowAttach", OffsetValue=OffsetValue, Origin=True, Object=Item, MovieAttach=True,
                           AddArrowChild=Mengine.hasTouchpad() is False)
            source.addFunction(hotspot.disable)
            source.addFunction(ClickHolder.set, self.itemSlots[self.AttachItem])

        # if self.AttachItem is not None:

        def holder_scopeClick(source_, slot_holder):
            source_.addScope(self._scopeSlotMovieSocketClick, slot_holder)

        source.addScope(holder_scopeClick, ClickHolder)

    def __scopeSetClickedSocket(self, source, slot_holder, allowed_slot_holder):
        slot = slot_holder.get()

        for (slot_name, movie), race in source.addRaceTaskList(slot.allowedMovies.iteritems()):
            allowed_slot = self.itemSlots[slot_name]
            if allowed_slot.state is True:
                race.addBlock()

            if movie.getType() == 'ObjectMovie':
                race.addTask('TaskMovieSocketClick', Movie=movie, SocketName='socket',
                             UseArrowFilter=False, isDown=True)
            elif movie.getType() == 'ObjectMovie2':
                race.addTask('TaskMovie2SocketClick', Movie2=movie, SocketName='socket',
                             UseArrowFilter=False, isDown=True)

            race.addFunction(allowed_slot_holder.set, self.itemSlots[slot_name])

    @staticmethod
    def __scopeInvalidClick(source, slot_holder):
        slot = slot_holder.get()

        source.addTask("TaskItemInvalidUse", Item=slot.Icon.Item)
        source.addDelay(0)

    def _resolveSocketClick(self, slot_holder, allowed_slot_holder, allowed_slot_used):
        allowed_slot_used.set(False)

        allowed_slot = allowed_slot_holder.get()
        if allowed_slot is None:
            return

        slot = slot_holder.get()
        if slot is allowed_slot:
            return

        slot_icon = slot.Icon
        allowed_slot_icon = allowed_slot.Icon

        temp = slot_icon.Item
        slot_icon.Item = allowed_slot_icon.Item
        allowed_slot_icon.Item = temp

        temp = slot_icon.Idle
        slot_icon.Idle = allowed_slot_icon.Idle
        allowed_slot_icon.Idle = temp

        slot.Node.addChild(slot_icon.Idle.getEntityNode())
        slot.Node.addChild(slot_icon.Silhouette.getEntityNode())

        iconIdleSpriteCenter = self.getSpriteCenter(slot_icon.Idle)
        iconSilhouetteSpriteCenter = self.getSpriteCenter(slot_icon.Silhouette)

        slot_icon.Idle.getEntityNode().setLocalPosition(Mengine.vec2f(0.0, 0.0) - iconIdleSpriteCenter)
        slot_icon.Silhouette.getEntityNode().setLocalPosition(Mengine.vec2f(0.0, 0.0) - iconSilhouetteSpriteCenter)

        allowed_slot.Node.addChild(allowed_slot_icon.Idle.getEntityNode())
        allowed_slot.Node.addChild(allowed_slot_icon.Silhouette.getEntityNode())

        iconIdleSpriteCenter = self.getSpriteCenter(allowed_slot_icon.Idle)
        iconSilhouetteSpriteCenter = self.getSpriteCenter(allowed_slot_icon.Silhouette)

        allowed_slot_icon.Idle.getEntityNode().setLocalPosition(Mengine.vec2f(0.0, 0.0) - iconIdleSpriteCenter)
        allowed_slot_icon.Silhouette.getEntityNode().setLocalPosition(
            Mengine.vec2f(0.0, 0.0) - iconSilhouetteSpriteCenter)
        allowed_slot_used.set(True)

    def _socketClickResult(self, source, slot_holder, allowed_slot_holder, result_holder, allowed_slot_used):
        slot = slot_holder.get()
        allowed_slot = allowed_slot_holder.get()
        result = result_holder.get()
        allowed_slot_used = allowed_slot_used.get()

        if allowed_slot_used:
            source.addTask("AliasRemoveItemAttach", Item=allowed_slot.Icon.Item)
            hotspot = allowed_slot.Icon.Item.entity.getHotSpot()
        else:
            source.addTask("AliasRemoveItemAttach", Item=slot.Icon.Item)
            hotspot = slot.Icon.Item.entity.getHotSpot()

        source.addNotify(Notificator.onSoundEffectOnObject, self.object, 'ItemCollect_Plassed')

        if self.AttachItem is not None:
            self.object.setParam('AttachItem', None)

        if result:
            source.addFunction(allowed_slot.enableIcon, True)
            source.addFunction(SystemItemCollect.addFoundItem, allowed_slot.ID)
            source.addNotify(Notificator.onItemCollectSetItem, slot.Icon.Item)
            source.addNotify(Notificator.onHintActionItemCollectEnd)

        source.addFunction(hotspot.enable)
        source.addFunction(self.stopItemSelectEffect)

    def _scopeSlotMovieSocketClick(self, source, slot_holder):
        result_holder = Holder()
        allowed_slot_holder = Holder()
        slot = slot_holder.get()
        self.attachItemToCursor_Cash = slot.Icon.Item
        allowed_slot_used = Holder()
        self.playItemSelectEffect(slot.Icon.Item)

        with source.addRaceTask(2) as (tc_valid, tc_invalid):
            tc_valid.addScope(self.__scopeSetClickedSocket, slot_holder, allowed_slot_holder)
            tc_valid.addFunction(result_holder.set, True)

            tc_invalid.addScope(self.__scopeInvalidClick, slot_holder)
            tc_invalid.addFunction(result_holder.set, False)

        source.addFunction(self._resolveSocketClick, slot_holder, allowed_slot_holder, allowed_slot_used)
        source.addScope(self._socketClickResult, slot_holder, allowed_slot_holder, result_holder, allowed_slot_used)

    def checkComplete(self):
        flag = True
        for slot in self.itemSlots.values():
            if slot.state is False:
                flag = False
        return flag

    def _cleanUp(self):
        if self.tc is not None:
            self.tc.cancel()
        self.tc = None

        self.attachItemToCursor = None
        if self.attachItemToCursor_Cash is not None:
            TaskManager.runAlias("AliasRemoveItemAttach", None, Item=self.attachItemToCursor_Cash)
        self.attachItemToCursor_Cash = None

        for slot in self.itemSlots.values():
            slot.Icon.Idle.getEntityNode().removeFromParent()
            slot.Icon.Silhouette.getEntityNode().removeFromParent()
            slot.Node.removeFromParent()
            slot.Movie.onDestroy()
        self.itemSlots = {}
        self.stopItemSelectEffect()

        if self._root is not None:
            self._root.removeFromParent()
            Mengine.destroyNode(self._root)
        self._root = None
