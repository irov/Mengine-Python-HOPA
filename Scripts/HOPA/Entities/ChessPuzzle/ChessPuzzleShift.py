from Functor import Functor

from ChessPuzzleElement import ChessPuzzleElement

class ChessPuzzleShift(ChessPuzzleElement):
    def __init__(self, dx, dy):
        super(ChessPuzzleShift, self).__init__()
        self.observer = None
        self.dx = dx
        self.dy = dy
        self.block = False
        pass

    def setBlock(self, value):
        self.block = value
        pass

    def initialize(self, grid, item):
        self.item = item
        entity = item.getEntity()
        sprite = entity.getSprite()
        size = sprite.getSurfaceSize()
        sprite.setLocalPosition((0, 0))
        self.node = entity
        self.node.setLocalPosition((-size.x / 2, -size.y / 2))
        self.observer = Notification.addObserver(Notificator.onItemClick, Functor(self._onItemClick, grid))
        pass

    def getDx(self):
        return self.dx
        pass

    def getDy(self):
        return self.dy
        pass

    def __repr__(self):
        return "C-> %i %i" % (self.dx, self.dy)
        pass

    def setActive(self, value):
        self.item.setInteractive(value)
        pass

    def isCanMove(self, dx, dy, nextElement):
        if self.dx == 0 and dx != 0:
            return False
            pass

        if self.dy == 0 and dy != 0:
            return False
            pass

        if nextElement is not None:
            return False
            pass

        return True
        pass

    def _updateView(self):
        self.setActive(True)
        pass

    def _onMove(self):
        self.setActive(False)
        pass

    def _onItemClick(self, item, x, y, grid):
        if self.block is True:
            return False
            pass

        if item is not self.item:
            return False
            pass

        x = self.getX()
        y = self.getY()
        dX = self.getDx()
        dY = self.getDy()

        isShifted = grid.shiftFromPoint(x, y, dX, dY)
        if isShifted is True:
            Notification.notify(Notificator.onChessTurn)
            pass
        else:
            grid.restore()
            pass

        return False
        pass

    def _onFinalise(self):
        if self.observer is not None:
            Notification.removeObserver(self.observer)
        self.observer = None
