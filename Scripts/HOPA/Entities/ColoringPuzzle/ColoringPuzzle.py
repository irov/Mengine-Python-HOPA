from Foundation.GroupManager import GroupManager
from Foundation.TaskManager import TaskManager
from HOPA.ColoringPuzzleManager import ColoringPuzzleManager

from ColoringPuzzleBrush import ColoringPuzzleBrush
from ColoringPuzzleFragment import ColoringPuzzleFragment
from ColoringPuzzlePalette import ColoringPuzzlePalette

class ColoringPuzzleColor(object):
    def __init__(self, colorId, colorName):
        self.colorId = colorId
        self.colorName = colorName

    def getColorId(self):
        return self.colorId

    def getColorName(self):
        return self.colorName


Enigma = Mengine.importEntity("Enigma")


class ColoringPuzzle(Enigma):

    @staticmethod
    def declareORM(Type):
        Enigma.declareORM(Type)
        Type.addAction("Mix")
        pass

    def __init__(self):
        super(ColoringPuzzle, self).__init__()
        self.brushes = {}
        self.GameData = None
        self.palette = {}
        self.fragments = {}
        self.colors = {}
        self.currentColor = None
        self.currentBrush = None
        self.onPaintSoundMovieName = "Movie2_OnPaintSound"
        self.BlockCursorSocketName = "Socket_BlockCursor"

        self.onSocketBlockCursorEnterObserver = None
        self.onSocketBlockCursorLeaveObserver = None

        self.arrow_radius_saved = None

    def finalize(self):
        for paletteId, palette in self.palette.items():
            palette.finalize()
            pass

        for fragmentId, fragment in self.fragments.items():
            fragment.finalize()
            pass

        if self.currentBrush is not None:
            self.currentBrush.hide()
            pass

        self.currentBrush = None
        self.brushes = {}
        self.GameData = None
        self.palette = {}
        self.fragments = {}
        self.currentColor = None

        if self.onSocketBlockCursorEnterObserver is not None:
            Notification.removeObserver(self.onSocketBlockCursorEnterObserver)
            self.onSocketBlockCursorEnterObserver = None
            pass

        if self.onSocketBlockCursorLeaveObserver is not None:
            Notification.removeObserver(self.onSocketBlockCursorLeaveObserver)
            self.onSocketBlockCursorLeaveObserver = None
            pass

        arrow_radius_curr = Mengine.getArrowNode()

        if arrow_radius_curr != self.arrow_radius_saved and self.arrow_radius_saved is not None:
            arrow.setRadius(self.arrow_radius_saved)
        self.arrow_radius_saved = None

    def _autoWin(self):
        self.finalize()
        self.enigmaComplete()
        pass

    def _stopEnigma(self):
        self.finalize()
        pass

    def _skipEnigma(self):
        self._autoWin()
        pass

    def getColor(self, colorId):
        return self.colors[colorId]
        pass

    def _onActivate(self):
        super(ColoringPuzzle, self)._onActivate()
        pass

    def _preparation(self):
        self.GameData = ColoringPuzzleManager.getGame(self.EnigmaName)

        for colorId, colorData in self.GameData.colors.items():
            color = ColoringPuzzleColor(colorId, colorData["ColorName"])
            self.colors[colorId] = color
            pass

        for paletteId, paletteData in self.GameData.palette.items():
            socketObject = self.object.getObject(paletteData["SocketObjectName"])

            palette = ColoringPuzzlePalette(paletteData["ColorId"], socketObject)
            self.palette[paletteId] = palette
            pass

        for fragmentId, fragmentData in self.GameData.fragments.items():
            socketName = fragmentData["SocketObjectName"]
            socketObject = self.object.getObject(socketName)

            stateObject = self.object.getObject(fragmentData["ObjectName"])
            fragment = ColoringPuzzleFragment(stateObject, socketObject)
            color = self.getColor(fragmentData["DefaultColorId"])
            fragment.setColor(color)
            self.fragments[fragmentId] = fragment
            pass

        for brushId, brushData in self.GameData.brushes.items():
            movieGroup = GroupManager.getGroup(brushData["GroupName"])
            movieObject = movieGroup.getObject(brushData["ObjectName"])
            movieObject.setEnable(False)
            brush = ColoringPuzzleBrush(movieObject)
            self.brushes[brushId] = brush
            pass

        arrow_radius_curr = Mengine.getArrowNode()

        if arrow_radius_curr != self.GameData.arrow_radius:
            arrow.setRadius(self.GameData.arrow_radius)
            self.arrow_radius_saved = arrow_radius_curr

    def _onDeactivate(self):
        super(ColoringPuzzle, self)._onDeactivate()
        self.finalize()
        pass

    def getBrushForColor(self, colorId):
        brushId = self.GameData.brushesToColor[colorId]
        brush = self.brushes[brushId]
        return brush
        pass

    def _onChangeColor(self, colorId):
        if self.currentColor == colorId:
            return
            pass

        tupleColor = (self.currentColor, colorId)
        s_tuple = tuple(sorted(tupleColor))
        mixResult = self.Mix.get(s_tuple)
        if mixResult is not None:
            colorId = mixResult
            pass
        self.currentColor = colorId
        self.updateBrush()
        pass

    def updateBrush(self):
        brush = self.getBrushForColor(self.currentColor)
        if self.currentBrush is not None:
            self.currentBrush.hide()
            pass

        self.currentBrush = brush
        self.currentBrush.show()
        pass

    def playOnPaintSoundMovie(self):
        if TaskManager.existTaskChain("ColoringPuzzle_OnPaintSound"):
            return
            pass

        with TaskManager.createTaskChain(Name="ColoringPuzzle_OnPaintSound", Group=self.object) as tc:
            tc.addTask("TaskMovie2Play", Movie2Name=self.onPaintSoundMovieName)
            pass
        pass

    def _onClickFragment(self, fragment):
        fragment_color = fragment.getColor()
        brush_color = self.getColor(self.currentColor)

        if fragment_color == brush_color:
            return

        fragment.setColor(brush_color)
        self.playOnPaintSoundMovie()
        self._checkComplete()
        pass

    def _checkComplete(self):
        for fragmentId, colorId in self.GameData.coloringRules.items():
            fragment = self.fragments[fragmentId]
            checkColor = fragment.getColor()

            if colorId != checkColor.getColorId():
                return False
                pass
            pass

        self.finalize()
        self.enigmaComplete()
        return False
        pass

    def _restoreEnigma(self):
        self._preparation()
        for paletteId, palette in self.palette.items():
            palette.initialize(self._onChangeColor)
            pass

        for fragmentId, fragment in self.fragments.items():
            fragment.initialize(self._onClickFragment)
            pass

        self.currentColor = self.GameData.startColorId
        self.updateBrush()

        if self.object.hasObject(self.BlockCursorSocketName) is True:
            self.onSocketBlockCursorEnterObserver = Notification.addObserver(Notificator.onSocketMouseEnter, self.onSocketEntered)
            self.onSocketBlockCursorLeaveObserver = Notification.addObserver(Notificator.onSocketMouseLeave, self.onSocketLeaved)
            pass
        pass

    def _playEnigma(self):
        self._preparation()
        for paletteId, palette in self.palette.items():
            palette.initialize(self._onChangeColor)
            pass

        for fragmentId, fragment in self.fragments.items():
            fragment.initialize(self._onClickFragment)
            pass

        self.currentColor = self.GameData.startColorId
        self.updateBrush()

        if self.object.hasObject(self.BlockCursorSocketName) is True:
            self.onSocketBlockCursorEnterObserver = Notification.addObserver(Notificator.onSocketMouseEnter, self.onSocketEntered)
            self.onSocketBlockCursorLeaveObserver = Notification.addObserver(Notificator.onSocketMouseLeave, self.onSocketLeaved)
            pass
        pass

    def onSocketEntered(self, socket):
        if socket is self.object.getObject(self.BlockCursorSocketName):
            self.currentBrush.show()
            # self.updateBrush()
            pass

        return False
        pass

    def onSocketLeaved(self, socket):
        if socket is self.object.getObject(self.BlockCursorSocketName):
            self.currentBrush.hide()
            pass

        return False
