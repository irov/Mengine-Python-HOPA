# from Grid import Grid
# from ChessPuzzleElement import CELL_ELEMENT_TYPE_TARGET,CELL_ELEMENT_TYPE_FIGURE,CELL_ELEMENT_TYPE_CONTROL
# from ChessPuzzleElement import ChessPuzzleTarget,ChessPuzzleFigure,ChessPuzzleControl

class ChessPuzzleBoard(object):
    def __init__(self, width, height):
        super(ChessPuzzleBoard, self).__init__()
        self.elements = []
        self.width = width
        self.height = height
        self.movedElements = []
        pass

    def restore(self):
        for element in self.movedElements:
            element.restore()
            pass
        pass

    def hasCell(self, x, y):
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return False
            pass
        return True
        pass

    def getElement(self, x, y):
        for element in self.elements:
            if element.getX() == x and element.getY() == y:
                return element
                pass
            pass
        return None
        pass

    def hasElement(self, x, y):
        for element in self.elements:
            if element.getX() == x and element.getY() == y:
                return True
                pass
            pass
        return False
        pass

    def setElement(self, x, y, element):
        if self.hasCell(x, y) is False:
            pass

        element.setX(x)
        element.setY(y)
        self.elements.append(element)
        pass

    def getRow(self, y, minX, maxX):
        row = []
        for element in self.elements:
            if element.getY() != y:
                continue
                pass

            if element.getX() >= minX and element.getX() <= maxX:
                row.append(element)
                pass
            pass

        row = sorted(row, key=lambda elem: elem.getX())
        return row
        pass

    def getColumn(self, x, minY, maxY):
        col = []
        for element in self.elements:
            if element.getX() != x:
                continue
                pass
            if element.getY() >= minY and element.getY() <= maxY:
                col.append(element)
                pass

            pass

        col = sorted(col, key=lambda elem: elem.getY())
        return col
        pass

    def shiftFromPoint(self, x, y, dx, dy):
        elements = []
        if dx != 0 and dy == 0:
            if dx < 0:
                elements = self.getRow(y, x, self.width - 1)
                pass
            else:
                elements = self.getRow(y, 0, x)
                elements.reverse()
                pass
            pass
        elif dy != 0 and dx == 0:
            if dy < 0:
                elements = self.getColumn(x, y, self.height - 1)
                pass
            else:
                elements = self.getColumn(x, 0, y)
                elements.reverse()
                pass
        else:
            return False
            pass

        state = self.doShift(elements, dx, dy)
        return state
        pass

    def doShift(self, elements, dx, dy):
        self.movedElements = []
        for element in elements:
            nextX = element.getX() + dx
            nextY = element.getY() + dy
            if self.hasCell(nextX, nextY) is False:
                return False
                pass

            if element.isMovable() is False:
                continue
                pass

            nextElement = self.getElement(nextX, nextY)
            if element.isCanMove(dx, dy, nextElement) is False:
                return False
                pass

            element.move(dx, dy)
            pass

        #        for element in self.movedElements:
        #            element.endMoving()
        #            pass

        return True
        pass

    def visitElements(self, visitor):
        for element in self.elements:
            visitor(element)
            pass
        pass