from Foundation.Initializer import Initializer

from Path import Path

class ChipElement(Initializer):
    def __init__(self):
        super(ChipElement, self).__init__()
        self.view = None
        self.block = False
        self.moving = None
        self.onMove = False
        self.homeSlot = None
        self.destinationSlot = None
        pass

    def __repr__(self):
        destination = str(self.destinationSlot)
        if self.destinationSlot is None:
            destination = "None"
            pass

        return "%s From %i To %s" % (self.__class__.__name__, int(self.homeSlot), destination)
        pass

    def _onInitialize(self, view):
        super(ChipElement, self)._onInitialize(view)

        self.view = view
        self.objectEntity = self.view.getEntity()
        self.size = self.view.getSize()

        self.hotspot = self.view.getHotSpot()
        self.hotspot.setEventListener(onHandleMouseButtonEvent=self._onMouseButtonEvent)
        pass

    def _onFinalize(self):
        super(ChipElement, self)._onFinalize()
        self.objectEntity.removeFromParent()
        pass

    def setBlock(self, value):
        self.block = value
        pass

    def isBlock(self):
        if self.block is False:
            return False
            pass

        return True
        pass

    def getHomeSlot(self):
        return self.homeSlot
        pass

    def getDestinationSlot(self):
        return self.destinationSlot
        pass

    def setHomeSlot(self, slot):
        self.homeSlot = slot
        pass

    def setDestinationSlot(self, slot):
        self.destinationSlot = slot
        pass

    def setPosition(self, position):
        self.objectEntity.node.setLocalPosition(position)
        pass

    def getNodeWorldPosition(self):
        return self.objectEntity.node.getWorldPosition()
        pass

    def getMovieNode(self):
        return self.objectEntity
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

    def isCanMove(self):
        connections = Path.getActiveConnects(self.homeSlot)
        if len(connections) == 0:
            return False
            pass
        return True
        pass

    def goToHome(self):
        connections = Path.getConnects(self.homeSlot)
        if len(connections) == 0:
            return False
            pass

        anyConnection = connections[0]
        moving = anyConnection[1]
        pos = moving.getSlotPosition(self.homeSlot)
        pos.x -= (self.size.x / 2)
        pos.y -= (self.size.y / 2)
        self.view.setPosition((pos.x, pos.y))
        pass

    def endWalking(self):
        Path.move(self.homeSlot, self.destinationSlot)
        self.setHomeSlot(self.destinationSlot)
        self.setDestinationSlot(None)
        pass
    pass