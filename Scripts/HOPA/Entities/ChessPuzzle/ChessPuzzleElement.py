# CELL_ELEMENT_TYPE_TARGET = "target"
# CELL_ELEMENT_TYPE_FIGURE = "figure"
# CELL_ELEMENT_TYPE_SHIFT_CONTROL = "shift_control"

class ChessPuzzleElement(object):
    def __init__(self):
        self.x = None
        self.y = None
        self.lastDX = None
        self.lastDY = None
        self.movable = True
        self.onMoveCallback = None
        self.node = None
        pass

    def finalize(self):
        self.node.removeFromParent()
        self._onFinalise()
        pass

    def _onFinalise(self):
        pass

    def setCoord(self, x, y):
        self.setX(x)
        self.setY(y)
        pass

    def setX(self, x):
        self.x = x
        pass

    def setY(self, y):
        self.y = y
        pass

    def getX(self):
        return self.x
        pass

    def getY(self):
        return self.y
        pass

    def getLastDX(self):
        return self.lastDX
        pass

    def getLastDY(self):
        return self.lastDY
        pass

    def isCanMove(self, dx, dy, nextElement):
        return True
        pass

    def isMovable(self):
        return self.movable
        pass

    def move(self, dx, dy):
        self.lastDX = dx
        self.lastDY = dy
        x = self.getX() + dx
        y = self.getY() + dy
        self.setCoord(x, y)

        self._onMove()

        if self.onMoveCallback is None:
            return
            pass

        self.onMoveCallback(self)
        pass

    def _onMove(self):
        pass

    def setOnMoveCallback(self, callback):
        self.onMoveCallback = callback
        pass

    def restore(self):
        x = self.getX() - self.lastDX
        y = self.getY() - self.lastDY
        self.setCoord(x, y)
        self.lastDX = None
        self.lastDY = None
        pass

    def updateView(self):
        self._updateView()
        pass

    def _updateView(self):
        pass

    def getNode(self):
        return self.node
        pass

    pass
