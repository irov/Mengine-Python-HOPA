from Notification import Notification

from ChipElement import ChipElement
from Path import Path


class ChipElementDragDrop(ChipElement):
    def __init__(self):
        super(ChipElementDragDrop, self).__init__()
        self.hotspot = None

        self.MouseButtonHandlerID = None
        self.MouseMoveHandlerID = None

        pass

    def _onInitialize(self, view):
        super(ChipElementDragDrop, self)._onInitialize(view)

        self.MouseButtonHandlerID = Mengine.addMouseButtonHandler(self._onGlobalMouseButtonEvent)
        self.MouseMoveHandlerID = Mengine.addMouseMoveHandler(self._onGlobalMouseMove)

        Mengine.enableGlobalHandler(self.MouseButtonHandlerID, False)
        Mengine.enableGlobalHandler(self.MouseMoveHandlerID, False)

        # self.objectEntity.setEventListener(onGlobalHandleMouseMove = self._onGlobalMouseMove, onGlobalHandleMouseButtonEvent = self._onGlobalMouseButtonEvent)
        # self.objectEntity.enableGlobalMouseEvent(False)

        self.offset = (0, 0)
        pass

    def _onFinalize(self):
        super(ChipElementDragDrop, self)._onFinalize()
        if self.hotspot is not None:
            self.hotspot.removeEventListener()
            self.hotspot = None
            pass

        self.refresh()
        Mengine.removeGlobalHandler(self.MouseButtonHandlerID)
        Mengine.removeGlobalHandler(self.MouseMoveHandlerID)
        # self.objectEntity.removeEventListener()
        self.objectEntity = None
        pass

    def refresh(self):
        if self.objectEntity is None:
            return
            pass

        self.onMove = False

        Mengine.enableGlobalHandler(self.MouseButtonHandlerID, False)
        Mengine.enableGlobalHandler(self.MouseMoveHandlerID, False)
        # self.objectEntity.enableGlobalMouseEvent(False)
        pass

    def getArrowPoint(self):
        arrowPos = Mengine.getCursorPosition()
        newPos = Mengine.vec2f(arrowPos.x - self.offset[0], arrowPos.y - self.offset[1])
        return newPos
        pass

    def makeArrowOffset(self):
        position = self.getNodeWorldPosition()
        arrowPos = Mengine.getCursorPosition()
        self.offset = (arrowPos.x - position[0] - self.size.x / 2, arrowPos.y - position[1] - self.size.y / 2)
        Notification.notify(Notificator.onChipsMoving)
        pass

    def _onGlobalMouseMove(self, event):
        if self.onMove is False:
            return
            pass

        pos = self.getArrowPoint()

        if self.moveTo(pos) is False:
            return
            pass

        if self.moving.isEndMoving(self.destinationSlot) is True:
            self.endWalking()
            Notification.notify(Notificator.onPlaceChip, self)
            pass

        return
        pass

    def _onGlobalMouseButtonEvent(self, event):
        if self.isInitialized() is False:
            return
            pass

        if event.button != 0:
            return
            pass

        if self.onMove is False:
            return
            pass

        if self.destinationSlot is None:
            self.refresh()
            return
            pass

        if self.moving.isEndMoving(self.destinationSlot) is False:
            nearestSlot = self.moving.getNearestSlot()
            self.moving.goTo(nearestSlot)
            if nearestSlot != self.destinationSlot:
                Path.swapSlots(self.homeSlot, self.destinationSlot)
                self.homeSlot = self.destinationSlot
                self.destinationSlot = nearestSlot
                pass

            self.endWalking()
            Notification.notify(Notificator.onPlaceChip, self)
            pass

        self.refresh()
        return
        pass

    def _onMouseButtonEvent(self, touchId, x, y, pressure, button, isDown, isPressed):
        # if hs != self.hotspot:
        #     return False
        #     pass

        if button != 0:
            return False
            pass

        if self.isBlock() is True:
            return False
            pass

        if isDown is False:
            self.refresh()
            return False
            pass

        if self.isCanMove() is False:
            return False
            pass

        self.makeArrowOffset()
        self.onMove = True
        Mengine.enableGlobalHandler(self.MouseButtonHandlerID, True)
        Mengine.enableGlobalHandler(self.MouseMoveHandlerID, True)
        # self.objectEntity.enableGlobalMouseEvent(True)

        return False
        pass

    def moveTo(self, position):
        connections = Path.getActiveConnects(self.homeSlot)
        if len(connections) == 0:
            return False
            pass

        return self.chooseConnection(connections, position)
        pass

    def chooseConnection(self, connections, position):
        # chose moving with minimal distance to arrow position
        sortedConnections = []
        for connection in connections:
            moving = connection[1]
            indexData = moving.getNearestIndex(position)
            sortedConnections.append((indexData, connection))
            pass

        sortedConnections = sorted(sortedConnections, key=lambda x: x[0][0])

        chosenConnection = sortedConnections[0]
        index = chosenConnection[0][1]
        connection = chosenConnection[1]
        moving = connection[1]

        moving.setFrame(index)
        self.setMoving(moving)
        self.destinationSlot = connection[0]
        return True
        pass

    pass
