from Segment import Segment
from SegmentsRoll import SegmentsRoll


class RollManager:
    segments = []
    rolls = []

    @staticmethod
    def createSegment(elements):
        segment = Segment(elements)
        RollManager.segments.append(segment)
        return len(RollManager.segments) - 1
        pass

    @staticmethod
    def getSegment(id):
        return RollManager.segments[id]
        pass

    @staticmethod
    def getRoll(id):
        return RollManager.rolls[id]
        pass

    @staticmethod
    def isUniqueValueOnSegments(segments, value):
        for segmentId in segments:
            segment = RollManager.getSegment(segmentId)
            if segment.isUniqueValue(value) == False:
                return False
                pass
            pass
        return True
        pass

    @staticmethod
    def createRoll(listOfSegments):
        roll = SegmentsRoll()
        for segmentId in listOfSegments:
            segment = RollManager.getSegment(segmentId)
            roll.addSegment(segment)
            pass

        RollManager.rolls.append(roll)
        return len(RollManager.rolls) - 1
        pass

    @staticmethod
    def moveRollCW(rollId):
        roll = RollManager.getRoll(rollId)
        roll.moveValuesCW()
        pass

    @staticmethod
    def moveRollCCW(rollId):
        roll = RollManager.getRoll(rollId)
        roll.moveValuesCCW()
        pass

    @staticmethod
    def getSegmentElements(segmentId):
        segment = RollManager.getSegment(segmentId)
        return segment.getElements()
        pass

    @staticmethod
    def getRollSegments(rollId):
        roll = RollManager.getRoll(rollId)
        return roll.segments
        pass

    @staticmethod
    def getRollElements(rollId):
        roll = RollManager.getRoll(rollId)
        elements = []
        for segment in roll.segments:
            elements.extend(segment.elements)
            pass
        return elements
        pass

    pass


"""
segment1 = RollManager.createSegment([SegmentSlot(0,0) ,SegmentSlot(1,1), SegmentSlot(2,2), SegmentSlot(3,3),SegmentSlot(4,4)])
segment2 = RollManager.createSegment([SegmentSlot(5,5)])
segment3 = RollManager.createSegment([SegmentSlot(6,6),SegmentSlot(7,7),SegmentSlot(8,8)])
segment4 = RollManager.createSegment([SegmentSlot(9,9)])
segment5 = RollManager.createSegment([SegmentSlot(10,10),SegmentSlot(11,11),SegmentSlot(12,12)])
segment6 = RollManager.createSegment([SegmentSlot(13,13),SegmentSlot(14,14),SegmentSlot(15,15),SegmentSlot(16,16)])

rollId = RollManager.createRoll([segment1,segment2,segment3,segment4])
roll2Id = RollManager.createRoll([segment5,segment2,segment6,segment4])

print (RollManager.getRollSegments(rollId))
RollManager.moveRollCW(rollId)
print (RollManager.getRollSegments(rollId))
RollManager.moveRollCCW(rollId)
print (RollManager.getRollSegments(rollId))

print("----------------")
print (RollManager.getRollSegments(rollId))
print (RollManager.getRollSegments(roll2Id))
RollManager.moveRollCCW(roll2Id)
print (RollManager.getRollSegments(rollId))
print (RollManager.getRollSegments(roll2Id))

#segment4 = RollManager.createSegment([9])
#segment5 = RollManager.createSegment([10,11,12])
#segment6 = RollManager.createSegment([13,14,15,16])
"""
"""
segment1 = RollManager.createSegment([0,1,2,3,4])
segment2 = RollManager.createSegment([5])
segment3 = RollManager.createSegment([6,7,8])
segment4 = RollManager.createSegment([9])
segment5 = RollManager.createSegment([10,11,12])
segment6 = RollManager.createSegment([13,14,15,16])

rollId = RollManager.createRoll([segment1,segment2,segment3,segment4])
roll2Id = RollManager.createRoll([segment5,segment2,segment6,segment4])

print (RollManager.getRollSegments(rollId))
RollManager.moveRollCW(rollId)
print (RollManager.getRollSegments(rollId))
RollManager.moveRollCCW(rollId)
print (RollManager.getRollSegments(rollId))

print("----------------")
print (RollManager.getRollSegments(rollId))
print (RollManager.getRollSegments(roll2Id))
RollManager.moveRollCCW(roll2Id)
print (RollManager.getRollSegments(rollId))
print (RollManager.getRollSegments(roll2Id))
"""
