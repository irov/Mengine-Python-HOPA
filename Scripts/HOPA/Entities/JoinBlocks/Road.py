class Road(object):
    def __init__(self):
        self.beginBlock = None
        self.pathHead = None
        self.slotIdList = []
        self.allSlotList = []
        self.endBlock = None
        pass
    def setBeginBlock(self, beginBlock):
        self.beginBlock = beginBlock
        pass

    def getBeginBlock(self):
        return self.beginBlock
        pass

    def setEndBlock(self, endBlock):
        self.endBlock = endBlock
        pass

    def getEndBlock(self):
        return self.EndBlock
        pass

    def setSlotIdList(self, slotIdList):
        self.slotIdList = slotIdList
        pass

    def getSlotIdList(self):
        return self.slotIdList
        pass

    def setAllSlotList(self, allSlotList):
        self.allSlotList = allSlotList
        pass

    def getAllSlotList(self):
        return self.allSlotList
        pass

    def setPathHead(self, pathHead):
        self.pathHead = pathHead
        pass

    def getPathHead(self):
        return self.pathHead
        pass

    def destroy(self):
        self.beginBlock.setState(False)
        self.beginBlock._blocked = False
        self.endBlock.setState(False)
        self.endBlock._blocked = False
        self.pathHead.destroy()
        for value in self.slotIdList:
            self.allSlotList.remove(value)
            pass
        pass