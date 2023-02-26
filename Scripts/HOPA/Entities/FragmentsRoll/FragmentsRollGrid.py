class FragmentsRollGrid(object):
    def __init__(self):
        super(FragmentsRollGrid, self).__init__()
        self.elements = []
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
        element.setX(x)
        element.setY(y)
        self.elements.append(element)
        pass

    def getRow(self, y):
        row = []
        for element in self.elements:
            if element.getY() != y:
                continue
                pass
            row.append(element)
        row = sorted(row, key=lambda elem: elem.getX())
        return row
        pass

    def getColumn(self, x):
        col = []
        for element in self.elements:
            if element.getX() != x:
                continue
                pass
            col.append(element)
            pass

        col = sorted(col, key=lambda elem: elem.getY())
        return col
        pass

    def rollFromPoint(self, x, y, dx, dy):
        elements = []
        if dx != 0 and dy == 0:
            if dx < 0:
                elements = self.getRow(y)
                elements.reverse()
                pass
            else:
                elements = self.getRow(y)
                pass
            pass
        elif dy != 0 and dx == 0:
            if dy < 0:
                elements = self.getColumn(x)
                elements.reverse()
                pass
            else:
                elements = self.getColumn(x)
                pass

        # print("---",elements)
        state = self.doRoll(elements, dx, dy)
        return state
        pass

    def doRoll(self, elements, dx, dy):
        firstElement = elements[0]

        firstX = firstElement.getX()
        firstY = firstElement.getY()

        countElements = len(elements)

        firstElements = elements[0: (countElements - 1)]
        for element in firstElements:
            nextX = element.getX() + dx
            nextY = element.getY() + dy
            element.setX(nextX)
            element.setY(nextY)
            pass

        lastElement = elements[countElements - 1]
        lastElement.setX(firstX)
        lastElement.setY(firstY)
        pass

    def visitElements(self, visitor):
        for element in self.elements:
            visitor(element)
            pass
        pass

    pass