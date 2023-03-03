from Foundation.Initializer import Initializer
from Notification import Notification
from Path import Path


THING_THAT_SHOULD_NOT_BE = 1000


class ChipsTransporter(Initializer):
    def __init__(self):
        super(ChipsTransporter, self).__init__()

        self.transporter = None
        self.slotFrom = None
        self.slotTo = None
        self.activeSlot = None
        self.observerPlaceChips = None
        self.chip = None
        pass

    def _onInitialize(self, transporter, slotFrom, slotTo, activeSlot):
        super(ChipsTransporter, self)._onInitialize()

        self.transporter = transporter.getEntity()
        self.slotFrom = slotFrom
        self.slotTo = slotTo
        self.activeSlot = None
        self.transporter.addClickObserver(self._onTransporterClick)
        self.observerPlaceChips = Notification.addObserver(Notificator.onPlaceChip, self._onPlaceChip)
        self.chip = None

        self.setActiveSlot(activeSlot)

        if activeSlot == self.slotFrom:
            Path.setSlotValue(self.slotTo, THING_THAT_SHOULD_NOT_BE)
            pass

        elif activeSlot == self.slotTo:
            Path.setSlotValue(self.slotFrom, THING_THAT_SHOULD_NOT_BE)
            pass
        pass

    def _onFinalize(self):
        super(ChipsTransporter, self)._onFinalize()

        Notification.removeObserver(self.observerPlaceChips)
        pass

    def goTo(self, slot):
        pass

    def isEndMoving(self, slot):
        if slot == self.activeSlot:
            return True
            pass
        return False
        pass

    def getDestinationSlot(self):
        if self.activeSlot == self.slotFrom:
            return self.slotTo
            pass
        return self.slotFrom
        pass

    def attach(self, chip):
        node = chip.getMovieNode()
        self.transporter.attachToMovie(node)
        self.chip = chip
        pass

    def detach(self, chip):
        if chip != self.chip:
            pass

        node = chip.getMovieNode()
        self.transporter.detachFromMovie(node)
        self.chip = None
        pass

    def _onPlaceChip(self, chip):
        if chip.getHomeSlot() != self.slotFrom and chip.getHomeSlot() != self.slotTo:
            return False
            pass
        chip.setMoving(self)
        return False
        pass

    def setActiveSlot(self, slot):
        if slot != self.slotFrom and slot != self.slotTo:
            return
            pass
        self.activeSlot = slot
        pass

    def getAngle(self):
        angle = self.transporter.getMovieSlotAngle()
        return angle

    def swap(self):
        if self.activeSlot is None:
            return
            pass

        if self.chip is not None:
            self.chip.setBlock(True)
            pass

        def refresh():
            self.transporter.setBlock(False)
            pass

        if self.activeSlot == self.slotFrom:
            self.transporter.setBlock(True)
            Path.swapSlots(self.slotFrom, self.slotTo)
            self.transporter.playForward(refresh)
            self.setActiveSlot(self.slotTo)
            pass
        else:
            Path.swapSlots(self.slotTo, self.slotFrom)
            self.transporter.setBlock(True)
            self.transporter.playBackward(refresh)
            self.setActiveSlot(self.slotFrom)
            pass

        if self.chip is not None:
            self.chip.setBlock(False)
            self.chip.setHomeSlot(self.activeSlot)
            pass
        pass

    def _onTransporterClick(self):
        self.swap()
        pass

    pass
