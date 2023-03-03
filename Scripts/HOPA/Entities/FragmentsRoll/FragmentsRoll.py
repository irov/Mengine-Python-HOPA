from Foundation.TaskManager import TaskManager
from Functor import Functor
from HOPA.FragmentsRollManager import FragmentsRollManager
from Notification import Notification

from FragmentsRollElementDragDrop import FragmentsRollElementDragDrop
from FragmentsRollGrid import FragmentsRollGrid
from FragmentsRollMovieGrid import FragmentsRollMovieGrid
from FragmentsRollMoving import FragmentsRollMoving


def getMaxMin(first, second):
    if first > second:
        return (first, second)
    else:
        return (second, first)


class FragmentsRollShift(object):
    def __init__(self, x, y, dx, dy):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.fragment = None
        pass

    def isForward(self):
        if self.dx < 0 or self.dy < 0:
            return False
            pass

        return True


Enigma = Mengine.importEntity("Enigma")


class FragmentsRoll(Enigma):
    def __init__(self):
        super(FragmentsRoll, self).__init__()
        self.fragments = {}
        self.movingFragments = []
        self.generatedObjects = []

        self.extraMovingFragments = []

        self.grid = None

        self.gridView = None

        self.GameData = None

        self.onFocusObserver = None

        self.gridMovieName = "Movie_Grid"

        self.horizontalForwardMovieName = "Movie_MoveRight"
        self.horizontalBackwardMovieName = "Movie_MoveLeft"
        self.verticalForwardMovieName = "Movie_MoveDown"
        self.verticalBackwardMovieName = "Movie_MoveUp"

        self.soundOnMoveMovieName = "Movie_Sound_OnMove"
        self.soundOnEndMovingMovieName = "Movie_Sound_OnEndMoving"

        self.currentShift = FragmentsRollShift(0, 0, 0, 0)
        pass

    def finalize(self):
        if self.onFocusObserver is not None:
            Notification.removeObserver(self.onFocusObserver)
            self.onFocusObserver = None
            pass

        for fragment in self.movingFragments:
            fragment.finalize()
            pass

        for fragmentId, fragment in self.fragments.items():
            fragment.finalize()
            pass

        for generatedObject in self.generatedObjects:
            generatedObject.removeFromParent()
            pass

        self.grid = None

        if self.gridView is not None:
            self.gridView.clear()
            self.gridView.finalize()
            self.gridView = None
            pass

        self.GameData = None

        self.generatedObjects = []
        self.fragments = {}
        self.movingFragments = []
        self.generatedObjects = []
        pass

    def _onDeactivate(self):
        super(FragmentsRoll, self)._onDeactivate()
        self.finalize()
        pass

    def _autoWin(self):
        self.enigmaComplete()
        pass

    def _stopEnigma(self):
        self.finalize()
        pass

    def _skipEnigma(self):
        self._autoWin()
        pass

    def _checkComplete(self):
        for fragmentId, fragment in self.fragments.items():
            fragmentData = self.GameData.rules[fragmentId]
            if fragment.getX() != fragmentData["X"] or fragment.getY() != fragmentData["Y"]:
                return
                pass
            pass

        self.enigmaComplete()
        return False
        pass

    def createObjectFromPrototype(self, prototypeName):
        countGen = len(self.generatedObjects)
        objectName = "%s_%i" % (prototypeName, countGen)
        obj = self.object.generateObject(objectName, prototypeName)
        self.generatedObjects.append(obj)
        return obj
        pass

    def initExtraFragment(self):
        if self.currentShift.isForward() is True:
            firstIndex = len(self.movingFragments) - 1
            lastIndex = 0
            pass
        else:
            firstIndex = 0
            lastIndex = len(self.movingFragments) - 1
            pass
        pass

        firstFragment = self.movingFragments[firstIndex]
        type = firstFragment.getType()
        lastFragment = self.movingFragments[lastIndex]

        fragment = self.generateFragment(type)

        shiftDx = -1 * self.currentShift.dx
        shiftDy = -1 * self.currentShift.dy
        fragmentX = lastFragment.getX() + shiftDx
        fragmentY = lastFragment.getY() + shiftDy

        fragment.setX(fragmentX)
        fragment.setY(fragmentY)

        self.extraMovingFragments.append(fragment)
        self.movingFragments.append(fragment)
        pass

    def setActiveMoving(self, movieName):
        soundMovie = self.object.getObject(self.soundOnMoveMovieName)
        for fragment in self.movingFragments:
            movie = self.createObjectFromPrototype(movieName)
            movieEntity = movie.getEntity()

            self.gridView.setNode(fragment.getX(), fragment.getY(), movieEntity)

            movieReverse = self.createObjectFromPrototype(movieName + "_Reverse")
            movieReverseEntity = movieReverse.getEntity()

            self.gridView.setNode(fragment.getX(), fragment.getY(), movieReverseEntity)

            moving = FragmentsRollMoving(movie, soundMovie, movieReverse)
            fragment.setMoving(moving)
            pass
        pass

    def initMovingFragments(self, fragment, dx, dy):
        # Check blind zone
        if abs(dx) == abs(dy):
            return False
            pass

        x = fragment.getX()
        y = fragment.getY()
        self.currentShift.fragment = fragment

        movieName = None

        if abs(dx) > abs(dy):
            self.currentShift.dy = 0
            self.movingFragments = self.grid.getRow(y)

            if dx < 0:
                self.currentShift.dx = -1
                movieName = self.horizontalBackwardMovieName
                pass
            else:
                self.currentShift.dx = 1
                movieName = self.horizontalForwardMovieName
                pass
        else:
            self.currentShift.dx = 0

            self.movingFragments = self.grid.getColumn(x)
            if dy < 0:
                self.currentShift.dy = -1
                movieName = self.verticalBackwardMovieName
                pass
            else:
                self.currentShift.dy = 1
                movieName = self.verticalForwardMovieName
                pass
            pass

        self.currentShift.x = x
        self.currentShift.y = y

        self.initExtraFragment()
        self.setActiveMoving(movieName)
        return True
        pass

    def checkCountMoving(self, isCancel):
        self.countMovings -= 1
        if self.countMovings > 0:
            return
            pass
        elif self.countMovings == 0:
            self.playOnEndSoundMovie()
            if isCancel is True:
                self.refresh()
                pass
            else:
                self.endMoving()
                pass
            pass
        pass

    def onInterruptMovingFragment(self, fragment):
        self.countMovings = len(self.movingFragments)

        cancel = False
        if fragment.isNearEnd() is False:
            cancel = True
            pass

        callback = Functor(self.checkCountMoving, cancel)

        for fragment in self.movingFragments:
            if cancel is True:
                fragment.moveToBegin(callback)
                pass
            else:
                fragment.moveToEnd(callback)
                pass
            pass
        pass

    def isOnMoving(self):
        if len(self.movingFragments) > 0:
            return True
            pass
        return False
        pass

    def refresh(self):
        self.blockFragments(False)
        self.gridView.refresh()

        for fragment in self.movingFragments:
            fragment.refresh()
            pass

        self.movingFragments = []

        for fragment in self.extraMovingFragments:
            fragment.finalize()
            pass

        self.extraMovingFragments = []
        pass

    def playOnEndSoundMovie(self):
        if TaskManager.existTaskChain("FragmentsRoll_SoundEndMoving"):
            return
            pass

        with TaskManager.createTaskChain(Name="FragmentsRoll_SoundEndMoving", Group=self.object) as tc:
            tc.addTask("TaskMoviePlay", MovieName=self.soundOnEndMovingMovieName)
            pass
        pass

    def onEndMovingFragment(self):
        self.playOnEndSoundMovie()
        self.endMoving()
        pass

    def endMoving(self):
        self.grid.rollFromPoint(self.currentShift.x, self.currentShift.y, self.currentShift.dx, self.currentShift.dy)
        self.refresh()
        self._checkComplete()
        pass

    def blockFragments(self, value):
        for fragmentId, fragment in self.fragments.items():
            fragment.setBlock(value)
            pass
        pass

    def onMoveFragment(self, fragment, dx, dy):
        if len(self.movingFragments) == 0:
            if self.initMovingFragments(fragment, dx, dy) is False:
                return
                pass

            self.blockFragments(True)
            pass

        isBackward = False

        if any([
            (self.currentShift.dy < 0 and dy > 0),
            (self.currentShift.dy > 0 and dy < 0),
            (self.currentShift.dx > 0 and dx < 0),
            (self.currentShift.dx < 0 and dx > 0)
        ]):
            isBackward = True
        else:
            isBackward = False

        for fragment in self.movingFragments:
            if isBackward is True:
                fragment.moveBackward()
            else:
                fragment.moveForward()

    def generateFragment(self, fragmentId):
        name = self.GameData.fragments[fragmentId]["ObjectName"]
        item = self.createObjectFromPrototype(name)
        fragment = FragmentsRollElementDragDrop(fragmentId, item)
        return fragment
        pass

    def _restoreEnigma(self):
        self.GameData = FragmentsRollManager.getGame(self.EnigmaName)

        gridMovieObject = self.object.getObject(self.gridMovieName)

        self.grid = FragmentsRollGrid()
        self.gridView = FragmentsRollMovieGrid(self.grid, gridMovieObject, self.GameData.cells)

        for fragmentId, fragmentData in self.GameData.fragments.items():
            fragment = self.generateFragment(fragmentId)

            self.grid.setElement(fragmentData["X"], fragmentData["Y"], fragment)
            self.fragments[fragmentId] = fragment
            pass

        self.refresh()
        self.onFocusObserver = Notification.addObserver(Notificator.onFocus, self._onFocus)

        for fragmentId, fragment in self.fragments.items():
            fragment.initialize(self)
            pass
        pass

    def _playEnigma(self):
        self.GameData = FragmentsRollManager.getGame(self.EnigmaName)

        gridMovieObject = self.object.getObject(self.gridMovieName)

        self.grid = FragmentsRollGrid()
        self.gridView = FragmentsRollMovieGrid(self.grid, gridMovieObject, self.GameData.cells)

        for fragmentId, fragmentData in self.GameData.fragments.items():
            fragment = self.generateFragment(fragmentId)

            self.grid.setElement(fragmentData["X"], fragmentData["Y"], fragment)
            self.fragments[fragmentId] = fragment
            pass

        self.refresh()
        self.onFocusObserver = Notification.addObserver(Notificator.onFocus, self._onFocus)

        for fragmentId, fragment in self.fragments.items():
            fragment.initialize(self)
            pass
        pass

    def _onFocus(self, value):
        if value is False:
            return False
            pass

        self.refresh()
        return False
