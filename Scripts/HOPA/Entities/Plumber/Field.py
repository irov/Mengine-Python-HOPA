from Foundation.TaskManager import TaskManager

from Cell import Cell

class Field(object):
    def __init__(self, startPos, data):
        self.metric = data.getMetric()
        self.cellMetric = data.getCellMetric()
        self.fieldData = data.getFieldData()
        self.itemData = data.getItemData()
        self.wallsData = data.getWallsData()
        self.startPos = startPos
        self.cells = {}
        pass

    def getCells(self):
        return self.cells
        pass

    def setupCells(self, object):
        cellWidth = self.cellMetric[0]
        cellHeight = self.cellMetric[1]

        for column in range(self.metric[0]):
            for row in range(self.metric[1]):
                cellPosition = (row, column)

                cellMoviePositionX = self.startPos[0] + (cellWidth * column)
                cellMoviePositionY = self.startPos[1] + (cellHeight * row)
                cellMoviePosition = (cellMoviePositionX, cellMoviePositionY)

                cellData = self.fieldData[row][column]
                if cellData != self.wallsData:
                    cellMovie = object.generateObject("Cell_%d_%d" % (row, column), "Movie_Cell")
                    cellMovie.setPosition(cellMoviePosition)
                    pass
                else:
                    cellMovie = object.generateObject("Cell_%d_%d" % (row, column), "Movie_Cell")
                    cellMovie.setPosition(cellMoviePosition)
                    TaskManager.runAlias("TaskMovieSocketEnable", None, SocketName="socket", Movie=cellMovie, Value=False)
                    pass
                cell = Cell(cellPosition, cellWidth, cellHeight, cellMovie, cellData)
                self.cells[(row, column)] = cell
                pass
            pass
        pass

    def setItemToCell(self, item):
        row = item.getRow()
        column = item.getColumn()

        cell = self.cells[row, column]
        cellMovie = cell.getMovie()
        cellMovieEntity = cellMovie.getEntity()

        itemMovie = item.getMovie()
        itemDirectionMovie = item.getDirectionMovie()

        itemMovieEntity = itemMovie.getEntity()

        itemDirectionMovieEntity = itemDirectionMovie.getEntity()

        itemDirectionMovieSlot = itemDirectionMovieEntity.getMovieSlot("slot")

        itemDirectionMovieSlot.addChild(itemMovieEntity)
        cellMovieEntity.addChild(itemDirectionMovieEntity)

        itemMovieEntity.setFirstFrame()
        itemDirectionMovieEntity.setFirstFrame()
        pass

    def onDrestroy(self):
        for cell in self.cells.values():
            cell.onDestroy()
            pass

        self.metric = None
        self.cellMetric = None
        self.fieldData = None
        self.itemData = None
        self.wallsData = None
        self.startPos = None
        self.cells = {}
        pass