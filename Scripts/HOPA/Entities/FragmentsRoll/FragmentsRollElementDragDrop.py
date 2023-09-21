from FragmentsRollElement import FragmentsRollElement


class FragmentsRollElementDragDrop(FragmentsRollElement):
    def __init__(self, type, item):
        super(FragmentsRollElementDragDrop, self).__init__(type)
        self.item = item

        self.entity = self.item.getEntity()
        self.entityNode = self.item.getEntityNode()
        self.size = self.entity.getSize()

        self.hotspot = None

        self.offset = (0, 0)
        self.game = None
        self.moving = None
        self.onMove = False

        self.block = False

        self.setPosition((-self.size.x / 2, -self.size.y / 2))
        self.Interact = False

        self.dxx = 0
        self.dyy = 0
        self.ddx = 0
        self.ddy = 0
        self.h = False

        self.MouseButtonHandlerID = None
        self.MouseMoveHandlerID = None

        pass

    def __repr__(self):
        return "Fr -> %s x:%s y:%s item" % (str(self.type), str(self.x), str(self.y))
        pass

    def initialize(self, game):
        self.game = game
        self.item.setEnable(True)

        if self.Interact is False:
            self.Interact = True
            self.item.setInteractive(True)
            pass

        self.hotspot = self.entity.getHotSpot()

        self.hotspot.setEventListener(onHandleMouseButtonEvent=self.__onMouseButtonEvent)
        self.hotspot.enable()

        self.MouseButtonHandlerID = Mengine.addMouseButtonHandler(self.__onGlobalMouseButtonEvent)
        self.MouseMoveHandlerID = Mengine.addMouseMoveHandler(self.__onGlobalMouseMove)

        Mengine.enableGlobalHandler(self.MouseButtonHandlerID, False)
        Mengine.enableGlobalHandler(self.MouseMoveHandlerID, False)

        # self.entity.setEventListener(onGlobalHandleMouseMove = self._onGlobalMouseMove, onGlobalHandleMouseButtonEvent = self._onGlobalMouseButtonEvent)
        # self.entity.enableGlobalMouseEvent(False)
        sprite = self.entity.getSprite()
        sprite.setLocalPosition((0, 0))
        pass

    def _onFinalise(self):
        if self.hotspot is not None:
            self.hotspot.removeEventListener()
            self.hotspot = None
            pass

        if (self.item is not None):
            if self.Interact is True:
                self.Interact = False
                self.item.setInteractive(False)
                pass
            self.item = None
            pass

        self.onMove = False

        if self.moving is not None:
            self.moving.detach(self)
            self.moving.finalize()
            self.moving = None
            pass

        if self.item is not None:
            # self.entity.removeEventListener()
            Mengine.removeGlobalHandler(self.MouseButtonHandlerID)
            Mengine.removeGlobalHandler(self.MouseMoveHandlerID)
            # self.entity.enableGlobalMouseEvent(False)

            self.entity = None
            self.entityNode = None
            pass
        pass

    def refresh(self):
        self.onMove = False
        if self.MouseButtonHandlerID is not None and self.MouseMoveHandlerID is not None:
            Mengine.enableGlobalHandler(self.MouseButtonHandlerID, False)
            Mengine.enableGlobalHandler(self.MouseMoveHandlerID, False)
        pass

    def setPosition(self, position):
        self.entityNode.setLocalPosition(position)
        pass

    def setBlock(self, value):
        self.block = value
        pass

    def isBlock(self):
        return self.block
        pass

    def moveForward(self):
        self.moving.moveForwardOneFrame()
        pass

    def moveBackward(self):
        self.moving.moveBackwardOneFrame()
        pass

    def moveToEnd(self, callback):
        self.moving.moveToEnd(callback)
        pass

    def moveToBegin(self, callback):
        self.moving.moveToBegin(callback)
        pass

    def isNearEnd(self):
        isNear = self.moving.isNearEnd()
        return isNear
        pass

    def __onGlobalMouseMove(self, event):
        if self.onMove is False:
            return

        if len(self.game.movingFragments) == 0:
            self.ddx += event.dx
            self.ddy += event.dy

            if -5 < self.ddx < 5 and -5 < self.ddy < 5:
                return

            self.dxx = self.ddx
            self.dyy = self.ddy

            ddx = self.ddx if self.ddx > 0 else -self.ddx
            ddy = self.ddy if self.ddy > 0 else -self.ddy

            if ddx > ddy:
                self.h = True
            else:
                self.h = False

            self.ddx = 0
            self.ddy = 0
        else:
            self.dxx += event.dx
            self.dyy += event.dy

        if self.h is True:
            if event.dx != 0.0:
                self.game.onMoveFragment(self, event.dx, 0)
        else:
            if event.dy != 0.0:
                self.game.onMoveFragment(self, 0, event.dy)

        if (self.h is True and self.dxx == 0) or (self.h is False and self.dyy == 0):
            self.game.refresh()
            self.ddx = 0
            self.ddy = 0
            self.dxx = 0
            self.dyy = 0
            self.h = False

        if self.moving.isEndMoving() is True:
            self.game.onEndMovingFragment()

            self.ddx = 0
            self.ddy = 0
            self.dxx = 0
            self.dyy = 0
            self.h = False

        return

    def __onGlobalMouseButtonEvent(self, event):
        if self.moving is None:
            return
            pass

        if event.button != 0:
            return
            pass

        if self.onMove is False:
            return
            pass

        self.game.onInterruptMovingFragment(self)
        self.refresh()
        return
        pass

    def setMoving(self, moving):
        if self.moving == moving:
            return False
            pass

        if self.moving is not None:
            self.moving.detach(self)
            pass

        self.setPosition((-self.size.x / 2, -self.size.y / 2))
        moving.attach(self)
        self.moving = moving
        return True
        pass

    def getNode(self):
        return self.entity.node
        pass

    def __onMouseButtonEvent(self, touchId, x, y, button, pressure, isDown, isPressed):
        if self.isBlock() is True:
            return False
            pass

        if button != 0:
            return False
            pass

        if isDown is False:
            self.refresh()
            return False
            pass

        self.onMove = True
        Mengine.enableGlobalHandler(self.MouseButtonHandlerID, True)
        Mengine.enableGlobalHandler(self.MouseMoveHandlerID, True)
        return False
        pass

    pass
