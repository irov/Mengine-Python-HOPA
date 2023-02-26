from HOPA.RotateAndSwapChipsManager import RotateAndSwapChipsManager
from Notification import Notification

from RotateAndSwapChipsConnection import RotateAndSwapChipsConnection
from RotateAndSwapChipsSlot import RotateAndSwapChipsSlot
from RotateAndSwapChipsSlotController import RotateAndSwapChipsSlotController
from RotateChipElement import RotateChipElement

Enigma = Mengine.importEntity("Enigma")

class RotateAndSwapChips(Enigma):
    def __init__(self):
        super(RotateAndSwapChips, self).__init__()
        self.chipElements = {}
        self.observer = None
        self.slots = {}
        self.connections = {}
        self.gridMovie = None
        self.slotsControllers = {}
        self.currentChip = None
        pass

    def finalize(self):
        for chipElementId, chipElement in self.chipElements.items():
            chipElement.finalize()
            pass

        for controllerId, controller in self.slotsControllers.items():
            controller.finalize()
            pass

        if self.observer != None:
            Notification.removeObserver(self.observer)
            pass

        self.chipElements = {}
        self.observer = None
        self.slots = {}
        self.connections = {}
        self.gridMovie = None
        self.slotsControllers = {}
        self.currentChip = None
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

    def _onPlaceChip(self, chip):
        self._checkComplete()
        return False
        pass

    #    def isCompleteChip(self,chipId):
    #        checkData = self.GameData.rules[chipId]
    #        chip = self.chipElements[chipId]
    #        angle = chip.getAngleInDegree()
    #        slotId = chip.getSlotId()
    #
    #        if  slotId != checkData["SlotId"]:
    #            return False
    #            pass
    #
    #        print "delta",Mengine.angle_delta_deg(angle,checkData["Angle"])
    #        if abs(Mengine.angle_delta_deg(angle,checkData["Angle"])) > 0.001 :
    #            print "Try Agian",chip.states.getName(),angle,checkData["Angle"],slotId,checkData["SlotId"]
    #            return False
    #            pass
    #
    #        return True
    #        pass

    def _checkComplete(self):
        #        isComplete = True
        #        for chipId,checkData in self.GameData.rules.items():
        #            chip = self.chipElements[chipId]
        #            if  self.isCompleteChip(chipId) is True:
        #                chip.setComplete(True)
        #                pass
        #            else:
        #                chip.setComplete(False)
        #                isComplete = False
        #                pass
        #            pass
        #
        #        if isComplete is False:
        #            return
        #            pass

        for chipId, checkData in self.GameData.rules.items():
            chip = self.chipElements[chipId]
            if chip.isComplete() is False:
                return
                pass
            pass

        # self.finalize()
        self.enigmaComplete()
        return False
        pass

    def _onActivate(self):
        super(RotateAndSwapChips, self)._onActivate()
        self.GameData = RotateAndSwapChipsManager.getGame(self.EnigmaName)

        gridMovieObject = self.object.getObject("Movie_Grid")
        gridMovieObject.setEnable(True)
        self.gridMovie = gridMovieObject.getEntity()

        for slotId, slotData in self.GameData.slots.items():
            MovieSlotName = slotData["MovieSlotName"]
            slotNode = self.gridMovie.getMovieSlot(MovieSlotName)
            slot = RotateAndSwapChipsSlot(slotId, slotNode)
            self.slots[slotId] = slot
            pass

        for controllerId, controllerData in self.GameData.slotsControllers.items():
            buttonObject = self.object.getObject(controllerData['ButtonName'])
            slot = self.slots[controllerData["SlotId"]]
            controller = RotateAndSwapChipsSlotController(slot, controllerData["DeltaAngle"], buttonObject)
            self.slotsControllers[controllerId] = controller
            pass

        for chipId, chipData in self.GameData.chips.items():
            statesObject = self.object.getObject(chipData["StatesObjectName"])
            rules = self.GameData.rules[chipId]

            chip = RotateChipElement(statesObject, rules["SlotId"], rules["Angle"])
            chip.setAngleInDegree(chipData["StartAngle"])
            slot = self.slots[chipData["StartSlotId"]]
            slot.setChip(chip)
            self.chipElements[chipId] = chip
            pass

        for connectionId, connectionData in self.GameData.connections.items():
            movie = self.object.getObject(connectionData['MovieObjectName'])
            connection = RotateAndSwapChipsConnection(movie)
            connectionSlots = self.GameData.connectionsSlots[connectionId]
            for connectionSlotData in connectionSlots:
                slotId = connectionSlotData["SlotId"]
                movieSlotName = connectionSlotData["MovieSlotName"]
                connection.setSlotIdentity(slotId, movieSlotName)
                pass

            self.connections[connectionId] = connection
            pass
        pass

    def _onDeactivate(self):
        super(RotateAndSwapChips, self)._onDeactivate()
        self.finalize()
        pass

    def findConnection(self, slot1Id, slot2Id):
        for connectionId, connection in self.connections.items():
            if connection.hasSlot(slot1Id) and connection.hasSlot(slot2Id):
                return connection
                pass
            pass
        return None
        pass

    def blockChips(self):
        for chipId, chip in self.chipElements.items():
            chip.setBlock(True)
            pass
        pass

    def unblockChips(self):
        for chipId, chip in self.chipElements.items():
            chip.setBlock(False)
            pass
        pass

    def swapChips(self, chip1, chip2):
        self.blockChips()
        slot1Id = chip1.getSlotId()
        slot2Id = chip2.getSlotId()
        # angle1 = chip1.getAngleInDegree()
        # angle2 = chip2.getAngleInDegree()

        connection = self.findConnection(slot1Id, slot2Id)
        connection.attachToSlot(slot1Id, chip1)
        # chip1.setAngleInDegree(angle1)
        connection.attachToSlot(slot2Id, chip2)
        # chip2.setAngleInDegree(angle2)

        def after():
            slot1 = self.slots[slot1Id]
            slot2 = self.slots[slot2Id]
            slot1.setChip(chip2)
            # chip2.setAngleInDegree(angle2)
            slot2.setChip(chip1)
            # chip1.setAngleInDegree(angle1)
            self._checkComplete()
            self.unblockChips()
            pass
        connection.move(after)
        pass

    def onClickChip(self, chip):
        if self.currentChip is None:
            self.currentChip = chip
            self.currentChip.setActive(True)
            pass
        elif self.currentChip is chip:
            self.currentChip.setActive(False)
            self.currentChip = None
            pass
        else:
            self.currentChip.setActive(False)
            self.swapChips(self.currentChip, chip)
            self.currentChip = None
            pass
        pass

    def _restoreEnigma(self):
        for chipId, chip in self.chipElements.items():
            chip.initialize(self.onClickChip)
            pass

        for controllerId, controller in self.slotsControllers.items():
            controller.initialize()
            pass

        self.observer = Notification.addObserver(Notificator.onPlaceChip, self._onPlaceChip)
        pass

    def _playEnigma(self):
        for chipId, chip in self.chipElements.items():
            chip.initialize(self.onClickChip)
            pass

        for controllerId, controller in self.slotsControllers.items():
            controller.initialize()
            pass

        self.observer = Notification.addObserver(Notificator.onPlaceChip, self._onPlaceChip)
        pass
    pass