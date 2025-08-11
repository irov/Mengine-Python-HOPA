from HOPA.ChessPuzzleManager import ChessPuzzleManager
from Notification import Notification

from ChessPuzzleBoard import ChessPuzzleBoard
from ChessPuzzleFigure import ChessPuzzleFigure
from ChessPuzzleMovieGrid import ChessPuzzleMovieGrid
from ChessPuzzleShift import ChessPuzzleShift


Enigma = Mengine.importEntity("Enigma")


class ChessPuzzle(Enigma):
    def __init__(self):
        super(ChessPuzzle, self).__init__()
        self.chessBoard = None
        self.boardView = None
        self.figures = []
        self.shifts = []
        self.targets = []
        self.GameData = None
        self.observer = None
        self.countMovingElements = 0
        self.generatedObjects = []
        self.horizontalForwardMovieName = "Movie_MoveHorizontalForward"
        self.horizontalBackwardMovieName = "Movie_MoveHorizontalBackward"
        self.verticalForwardMovieName = "Movie_MoveVerticalForward"
        self.verticalBackwardMovieName = "Movie_MoveVerticalBackward"
        pass

    ####################################################################

    def _stopEnigma(self):
        self.finalize()
        pass

    def moveElementOnMovie(self, element):
        dx = element.getLastDX()
        dy = element.getLastDY()
        x = element.getX()
        y = element.getY()
        movieName = None
        self.countMovingElements += 1
        if dy == 0:
            if dx < 0:
                movieName = self.horizontalBackwardMovieName
            else:
                movieName = self.horizontalForwardMovieName
            pass
        else:
            if dy < 0:
                movieName = self.verticalBackwardMovieName
            else:
                movieName = self.verticalForwardMovieName
            pass

        movie = self.createObjectFromPrototype(movieName)
        movieEntity = movie.getEntity()
        animatable = movieEntity.getAnimatable()
        node = element.getNode()

        def onCompleteMoving():
            element.updateView()
            self.countMovingElements -= 1

            if self.countMovingElements == 0:
                self.blockShifts(False)
                self._checkComplete()
                pass
            pass

        self.boardView.moveNode(x, y, node, movie, onCompleteMoving)
        pass

    def onMovePuzzleElement(self, element):
        if element in self.figures:
            if self.isPlacedFigure(element):
                element.setPlaced(True)
                pass
            else:
                element.setPlaced(False)
            pass
        self.moveElementOnMovie(element)
        pass

    def isPlacedFigure(self, figure):
        for targetData in self.targets:
            target = targetData["Data"]
            if target["x"] == figure.getX() and target["y"] == figure.getY():
                return True
                pass
            pass
        return False
        pass

    def blockShifts(self, value):
        for shift in self.shifts:
            shift.setBlock(value)
            pass
        pass

    def onChessTurn(self):
        self.blockShifts(True)
        return False
        pass

    def _checkComplete(self):
        for targetData in self.targets:
            target = targetData["Data"]
            element = self.chessBoard.getElement(target["x"], target["y"])
            if element is None:
                return
                pass

            if element not in self.figures:
                return
                pass
            pass

        self.enigmaComplete()
        return
        pass

    def _onActivate(self):
        super(ChessPuzzle, self)._onActivate()

        pass

    def _onDeactivate(self):
        super(ChessPuzzle, self)._onDeactivate()
        pass

    def _playEnigma(self):
        self.GameData = ChessPuzzleManager.getGame(self.EnigmaName)
        self.createGrid()
        self.createTargets()
        self.createFigures()
        self.createShifts()
        self.boardView.refresh()

        self.observer = Notification.addObserver(Notificator.onChessTurn, self.onChessTurn)

        for shift in self.shifts:
            shift.setActive(True)
            pass
        pass

    def finalize(self):
        for shift in self.shifts:
            shift.finalize()
            pass

        for figure in self.figures:
            figure.finalize()
            pass

        for targetData in self.targets:
            node = targetData["Node"]
            node.removeFromParent()
            pass

        if self.observer is not None:
            Notification.removeObserver(self.observer)
            pass

        for obj in self.generatedObjects:
            self.releaseCreatedObject(obj)
            pass

        self.chessBoard = None
        self.boardView = None
        self.figures = []
        self.shifts = []
        self.targets = []
        self.GameData = None
        self.observer = None
        self.countMovingElements = 0
        self.generatedObjects = []
        pass

    #############################################################

    def createGrid(self):
        boardWidth = self.GameData.grid.width
        boardHeight = self.GameData.grid.height
        self.chessBoard = ChessPuzzleBoard(boardWidth, boardHeight)
        self.boardView = ChessPuzzleMovieGrid(self.object, self.chessBoard, self.GameData.grid)
        pass

    def createObjectFromPrototype(self, prototypeName):
        ID = len(self.generatedObjects)
        objectName = "%s_%i" % (prototypeName, ID)
        obj = self.object.generateObject(objectName, prototypeName)
        self.generatedObjects.append(obj)
        return obj
        pass

    def releaseCreatedObject(self, obj):
        obj.onDestroy()
        pass

    def initElement(self, element):
        element.setOnMoveCallback(self.onMovePuzzleElement)
        pass

    def createShifts(self):
        for shiftId, shiftData in self.GameData.shifts.items():
            item = self.createObjectFromPrototype(shiftData['prototype'])
            shift = ChessPuzzleShift(shiftData['dX'], shiftData['dY'])
            shift.initialize(self.chessBoard, item)
            self.initElement(shift)
            self.chessBoard.setElement(shiftData['x'], shiftData['y'], shift)
            self.shifts.append(shift)
            pass
        pass

    def createFigures(self):
        for figureId, figureData in self.GameData.figures.items():
            states = self.createObjectFromPrototype(figureData['prototype'])
            figure = ChessPuzzleFigure(figureData['figureType'])
            self.initElement(figure)
            figure.initialize(states)
            self.chessBoard.setElement(figureData['x'], figureData['y'], figure)
            self.figures.append(figure)
            pass
        pass

    def createTargets(self):
        for targetID, targetData in self.GameData.targets.items():
            obj = self.createObjectFromPrototype(targetData['prototype'])
            entity = obj.getEntity()
            self.addChild(entity)
            sprite = entity.getSprite()
            size = sprite.getSurfaceSize()
            sprite.setLocalPosition((0, 0))
            entity.setLocalPosition((-size.x / 2, -size.y / 2))
            self.boardView.setNode(targetData['x'], targetData['y'], entity)
            self.targets.append(dict(Data=targetData, Node=entity))
