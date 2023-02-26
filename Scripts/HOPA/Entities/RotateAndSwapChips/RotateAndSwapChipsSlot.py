class RotateAndSwapChipsSlot(object):
    def __init__(self, slotId, slotNode):
        self.node = slotNode
        self.slotId = slotId
        self.chip = None
        pass

    def setChip(self, chip):
        if self.chip is chip:
            return
            pass

        self.chip = chip
        self.chip.attachTo(self.node)
        self.chip.setSlotId(self.slotId)
        pass

    def getChip(self):
        return self.chip
        pass

    def startRotation(self):
        if self.chip is None:
            return
            pass

        self.chip.setRotate(True)
        pass

    def stopRotation(self):
        if self.chip is None:
            return
            pass

        self.chip.setRotate(False)
        pass

    def rotate(self, angle):
        self.chip.rotateOnAngleInDegree(angle)
        pass
    pass