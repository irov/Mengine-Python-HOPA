from Foundation.TaskManager import TaskManager

class LetItSlideElement(object):
    def __init__(self, id, movieObject, isHorizontal, socket, length, field):
        self.id = id
        self.movieObject = movieObject
        self.isHorizontal = isHorizontal
        self.movieSocket = socket
        self.length = length

        self.field = field
        self.cells = []
        self.position = None
        self.mousePos = None
        pass

    def getPosition(self):
        return self.position
        pass

    def setPosition(self, position):
        if self.position is not None and position != self.position:
            collision = self.checkCollision(position)
        else:
            collision = True
            pass

        if position != self.position and collision is True:
            if self.position is not None:
                oldCells = self.getCellsForItem(self.field, self.position)
                self.setupEmptyCells(oldCells, True)
                pass

            self.position = position

            self.cells = self.getCellsForItem(self.field, self.position)
            positionForMovie = self.cells[0].getWorldPosition()

            self.updateMoviePosition(positionForMovie)

            self.setupEmptyCells(self.cells, False)

            Notification.notify(Notificator.onLetItSlideWin, self.id, self.position)
            pass
        pass

    def checkCollision(self, newPosition):
        nextCells = self.getCellsForItem(self.field, newPosition)

        for cell in nextCells:
            if cell not in self.cells:
                if cell.getEmpty() is False:
                    return False
                    pass
                pass
            pass
        return True
        pass

    def updateMoviePosition(self, newMoviePos):
        if self.movieObject.getPosition() == (0.0, 0.0, 0.0):
            self.movieObject.setPosition(newMoviePos)
            pass
        else:
            movieEntity = self.movieObject.getEntity()

            speed = 800

            TaskManager.runAlias("TaskNodeMoveTo", None, Node=movieEntity, To=newMoviePos, Speed=speed)
            pass
        pass

    def setupEmptyCells(self, cells, isEmpty):
        for cell in cells:
            cell.setEmpty(isEmpty)
            pass
        pass

    def getCellsForItem(self, field, position):
        cells = []
        if self.length > 1:
            posX = position[0]
            posY = position[1]

            for iterator in range(self.length):
                cell = field.getCellByPosition((posX, posY))
                cells.append(cell)
                if self.isHorizontal is True:
                    posY += 1
                    pass
                elif self.isHorizontal is False:
                    posX += 1
                    pass
                pass
            pass
        else:
            cell = field.getCellByPosition(position)
            cells.append(cell)
            pass
        return cells
        pass

    def onActivate(self):
        self.movieSocket.setEventListener(onHandleMouseButtonEvent=self._onMouseButtonEvent)
        self.movieSocket.setEventListener(onGlobalHandleMouseMove=self._onGlobalMouseMove,
                                          onGlobalHandleMouseButtonEvent=self._onGlobalMouseButtonEvent)
        pass

    def onDeactivate(self):
        pass

    def _onMouseButtonEvent(self, context, event):
        if event.button != 0:
            return False

        if event.isDown is True:
            self.movieSocket.enableGlobalMouseEvent(True)
            pass

        return True
        pass

    def _onGlobalMouseMove(self, event):
        arrowPosX = event.position.world.x
        arrowPosY = event.position.world.y

        currentMousePos = (arrowPosX, arrowPosY)

        if self.mousePos is None:
            self.mousePos = currentMousePos
            pass

        posX = self.position[0]
        posY = self.position[1]

        if arrowPosX - self.mousePos[0] > 60:
            posY += 1
            self.mousePos = currentMousePos
            pass
        elif arrowPosX - self.mousePos[0] < -60:
            self.mousePos = currentMousePos

            posY -= 1
            pass
        elif arrowPosY - self.mousePos[1] > 60:
            posX += 1
            self.mousePos = currentMousePos
            pass
        elif arrowPosY - self.mousePos[1] < -60:
            posX -= 1
            self.mousePos = currentMousePos
            pass
        else:
            pass

        newPosition = (posX, posY)

        if newPosition != self.position:
            self.setPosition(newPosition)
            pass

        return
        pass

    def _onGlobalMouseButtonEvent(self, event):
        if event.button != 0:
            return False

        if event.isDown is False:
            self.movieSocket.enableGlobalMouseEvent(False)
            self.mousePos = None
            pass
        pass

    def Destroy(self):
        self.movieSocket.enableGlobalMouseEvent(False)

        self.id = None
        self.movieObject = None
        self.isHorizontal = None
        self.movieSocket = None
        self.length = None

        self.field = None
        self.cells = []
        self.position = None
        self.mousePos = None
        pass

    pass
