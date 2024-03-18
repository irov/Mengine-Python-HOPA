from Foundation.GroupManager import GroupManager
from HOPA.PathChipsCryptManager import PathChipsCryptManager
from Notification import Notification

from ChipElementAuto import ChipElementAuto
from ChipElementDragDrop import ChipElementDragDrop
from ChipView import ChipView
from ChipsMoving import ChipsMoving
from ChipsTransporter import ChipsTransporter
from Path import Path


Enigma = Mengine.importEntity("Enigma")


class PathChipsCrypt(Enigma):
    def __init__(self):
        super(PathChipsCrypt, self).__init__()
        self.chipElements = []
        self.transporters = []
        self.chipViews = []
        self.observerPlaceChip = None
        self.observerBeginMovingChip = None
        self.completeEffects = {}
        self.chipCounter = 0
        self.generatedObjects = []
        self.movieSoundMoveChipName = "Movie2_Sound_MoveChip"
        pass

    def finalise(self):
        for chipElement in self.chipElements:
            chipElement.onFinalize()
            pass

        for chipView in self.chipViews:
            chipView.onFinalize()
            pass

        for transporter in self.transporters:
            transporter.onFinalize()
            pass

        if self.observerPlaceChip is not None:
            Notification.removeObserver(self.observerPlaceChip)
            self.observerPlaceChip = None
            pass

        if self.observerBeginMovingChip is not None:
            Notification.removeObserver(self.observerBeginMovingChip)
            self.observerBeginMovingChip = None
            pass

        for generatedObject in self.generatedObjects:
            generatedObject.removeFromParent()
            generatedObject.onDestroy()
            pass

        self.chipViews = []
        self.generatedObjects = []
        self.transporters = []
        self.chipElements = []
        pass

    def _autoWin(self):
        self.enigmaComplete()
        pass

    def _stopEnigma(self):
        self.finalise()
        pass

    def _resetEnigma(self):
        self.finalise()
        self._playEnigma()
        pass

    def _skipEnigma(self):
        self._autoWin()
        pass

    def setCompleteEffects(self):
        for slotId, chip in self.GameData.rules.items():
            if slotId not in self.completeEffects:
                continue
                pass

            value = Path.getSlotValue(slotId)
            completeMovie = self.completeEffects[slotId]
            isEnable = completeMovie.getParam("Enable")

            if value != chip:
                if isEnable is True:
                    completeMovie.setParam("Enable", False)
                    pass
                continue
                pass

            if isEnable is True:
                continue
                pass

            completeMovie.setParam("Enable", True)
            completeMovie.setParam("Loop", True)
            completeMovie.setParam("Play", True)
            pass
        pass

    def _onPlaceChip(self, chip):
        self._checkComplete()
        self.blockElements(False)
        return False
        pass

    def blockElements(self, value):
        for chipElement in self.chipElements:
            chipElement.setBlock(value)
            pass
        pass

    def _onBeginMovingChip(self, chip):
        self.blockElements(True)
        return False
        pass

    def _checkComplete(self):
        self.setCompleteEffects()

        for slotId, chips in self.GameData.rules.items():
            value = Path.getSlotValue(slotId)
            if value not in chips:
                return
                pass

        self.enigmaComplete()
        pass

    def createChip(self, chipId):
        chipData = self.GameData.chips[chipId]
        self.chipCounter += 1
        objName = "%s_%i" % (chipData["ObjectName"], self.chipCounter)
        chipStates = self.object.generateObject(objName, chipData["ObjectName"])
        chipView = ChipView()
        chipView.onInitialize(chipStates)
        self.chipViews.append(chipView)

        self.generatedObjects.append(chipStates)

        if chipData["MovingPolicy"] == "AutoPlay":
            chip = ChipElementAuto()
            chip.onInitialize(chipView)
            pass
        elif chipData["MovingPolicy"] == "DragDrop":
            chip = ChipElementDragDrop()
            chip.onInitialize(chipView)
            pass
        else:
            return None
            pass

        return chip
        pass

    def _onActivate(self):
        super(PathChipsCrypt, self)._onActivate()
        pass

    def _onDeactivate(self):
        super(PathChipsCrypt, self)._onDeactivate()

        self.finalise()
        pass

    def resetPositions(self):
        for chip in self.chipElements:
            chip.goToHome()
            pass
        pass

    def _restoreEnigma(self):
        self.GameData = PathChipsCryptManager.getGame(self.EnigmaName)
        for slotId, chipId in self.GameData.slots.items():
            if chipId == -1:
                Path.addSlot(slotId, None)
                continue
                pass

            chip = self.createChip(chipId)

            chip.setHomeSlot(slotId)
            Path.addSlot(slotId, chipId)
            self.chipElements.append(chip)
            pass

        for connection in self.GameData.connections:
            slotFrom = connection[0]
            slotTo = connection[1]
            movieName = connection[2]
            movie = self.object.getObject(movieName)
            pathMovie = ChipsMoving(movie, slotFrom, slotTo, self.movieSoundMoveChipName)
            Path.connect(slotFrom, slotTo, pathMovie)
            pass

        for connection in self.GameData.transporters:
            slotFrom = connection[0]
            slotTo = connection[1]
            activeSlot = connection[2]
            transporterName = connection[3]
            transporterDemon = self.object.getObject(transporterName)

            transporter = ChipsTransporter()
            transporter.onInitialize(transporterDemon, slotFrom, slotTo, activeSlot)

            self.transporters.append(transporter)
            pass

        for slotId, movieData in self.GameData.completeEffects.items():
            group = GroupManager.getGroup(movieData["GroupName"])
            completeMovie = group.getObject(movieData["ObjectName"])
            completeMovie.setParam("Enable", False)
            self.completeEffects[slotId] = completeMovie
            pass

        self.resetPositions()

        for chip in self.chipElements:
            if chip.isInitialized():
                continue
            chip.onInitialize()
            pass

        self.setCompleteEffects()

        self.observerPlaceChip = Notification.addObserver(Notificator.onPlaceChip, self._onPlaceChip)
        self.observerBeginMovingChip = Notification.addObserver(Notificator.onBeginMovingChip, self._onBeginMovingChip)
        pass

    def _playEnigma(self):
        self.GameData = PathChipsCryptManager.getGame(self.EnigmaName)
        for slotId, chipId in self.GameData.slots.items():
            if chipId == -1:
                Path.addSlot(slotId, None)
                continue
                pass

            chip = self.createChip(chipId)

            chip.setHomeSlot(slotId)
            Path.addSlot(slotId, chipId)
            self.chipElements.append(chip)
            pass

        for connection in self.GameData.connections:
            slotFrom = connection[0]
            slotTo = connection[1]
            movieName = connection[2]
            movie = self.object.getObject(movieName)
            pathMovie = ChipsMoving(movie, slotFrom, slotTo, self.movieSoundMoveChipName)
            Path.connect(slotFrom, slotTo, pathMovie)
            pass

        for connection in self.GameData.transporters:
            slotFrom = connection[0]
            slotTo = connection[1]
            activeSlot = connection[2]
            transporterName = connection[3]
            transporterDemon = self.object.getObject(transporterName)

            transporter = ChipsTransporter()
            transporter.onInitialize(transporterDemon, slotFrom, slotTo, activeSlot)

            self.transporters.append(transporter)
            pass

        for slotId, movieData in self.GameData.completeEffects.items():
            group = GroupManager.getGroup(movieData["GroupName"])
            completeMovie = group.getObject(movieData["ObjectName"])
            completeMovie.setParam("Enable", False)
            self.completeEffects[slotId] = completeMovie
            pass

        self.resetPositions()

        for chip in self.chipElements:
            if chip.isInitialized():
                continue
            chip.onInitialize()
            pass

        self.setCompleteEffects()

        self.observerPlaceChip = Notification.addObserver(Notificator.onPlaceChip, self._onPlaceChip)
        self.observerBeginMovingChip = Notification.addObserver(Notificator.onBeginMovingChip, self._onBeginMovingChip)
        pass

    pass
