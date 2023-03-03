class Cell(object):
    def __init__(self, isEmpty, position, worldPosition, top, bottom, left, right):
        self.isEmpty = isEmpty
        self.position = position
        self.worldPosition = worldPosition

        self.top = top
        self.bottom = bottom
        self.left = left
        self.right = right
        pass

    def getTop(self):
        return self.top
        pass

    def getBottom(self):
        return self.bottom
        pass

    def getLeft(self):
        return self.left
        pass

    def getRight(self):
        return self.right
        pass

    def getEmpty(self):
        return self.isEmpty
        pass

    def setEmpty(self, value):
        self.isEmpty = value
        pass

    def getPosition(self):
        return self.position
        pass

    def getWorldPosition(self):
        return self.worldPosition
        pass

    def Destroy(self):
        self.isEmpty = None
        self.position = None
        self.worldPosition = None

        self.top = None
        self.bottom = None
        self.left = None
        self.right = None
        pass

    pass


class Field(object):
    def __init__(self, gameData):
        self.fieldData = gameData.getFieldData()
        self.metric = gameData.getMetric()
        self.cellMetric = gameData.getCellMetric()
        self.cells = {}
        pass

    def setupField(self, startPosition):
        for row in range(self.metric[0]):
            for column in range(self.metric[1]):
                cellPosition = (row, column)
                cellWorldPositionX = startPosition[0] + (cellPosition[1] * self.cellMetric[0])
                cellWorldPositionY = startPosition[1] + (cellPosition[0] * self.cellMetric[1])

                cellTop = cellWorldPositionY
                cellLeft = cellWorldPositionX
                cellBottom = cellWorldPositionY + self.cellMetric[1]
                cellRight = cellWorldPositionX + self.cellMetric[0]

                cellWorldPosition = (cellWorldPositionX, cellWorldPositionY)
                isEmpty = bool(self.fieldData[row][column])
                cell = Cell(isEmpty, cellPosition, cellWorldPosition, cellTop, cellBottom, cellLeft, cellRight)

                self.cells[cellPosition] = cell
                pass
            pass
        pass

    def getCells(self):
        return self.cells
        pass

    def getCellByPosition(self, position):
        for cell in self.cells.values():
            if position == cell.getPosition():
                return cell
                pass
            pass
        return None
        pass

    def Destroy(self):
        for cell in self.cells.values():
            cell.Destroy()
            pass
        self.fieldData = None
        self.metric = None
        self.cellMetric = None
        self.cells = None
        pass
