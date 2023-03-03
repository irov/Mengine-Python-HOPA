class SegmentsRoll(object):
    def __init__(self):
        self.segments = []
        pass

    def addSegment(self, segment):
        self.segments.append(segment)
        pass

    def swapSegmentsCW(self, segmentFrom, segmentTo):
        element = segmentFrom.popLast()
        segmentTo.pushFront(element)
        pass

    def swapSegmentsCCW(self, segmentFrom, segmentTo):
        element = segmentFrom.popFirst()
        segmentTo.pushBack(element)
        pass

    def moveValuesCW(self):
        roll = SegmentsRoll()
        newValues = []
        for segment in self.segments:
            values = segment.getValues()

            newValues.append(values)
            roll.addSegment(values)
            pass
        roll.moveCW()
        for index, newValue in enumerate(newValues):
            self.segments[index].setValues(newValue)
            pass
        pass

    def moveValuesCCW(self):
        roll = SegmentsRoll()
        newValues = []
        for segment in self.segments:
            values = segment.getValues()

            newValues.append(values)
            roll.addSegment(values)
            pass
        roll.moveCCW()
        for index, newValue in enumerate(newValues):
            self.segments[index].setValues(newValue)
            pass
        pass

    def moveCW(self):
        count = len(self.segments)
        for index in range(0, count - 1):
            segmentFrom = self.segments[index]
            segmentTo = self.segments[index + 1]
            self.swapSegmentsCW(segmentFrom, segmentTo)
            pass
        segmentFrom = self.segments[count - 1]
        segmentTo = self.segments[0]
        self.swapSegmentsCW(segmentFrom, segmentTo)
        pass

    def moveCCW(self):
        count = len(self.segments)
        for index in reversed(range(1, count)):
            segmentFrom = self.segments[index]
            segmentTo = self.segments[index - 1]
            self.swapSegmentsCCW(segmentFrom, segmentTo)
            pass

        segmentFrom = self.segments[0]
        segmentTo = self.segments[count - 1]
        self.swapSegmentsCCW(segmentFrom, segmentTo)
        pass

    pass
