from Foundation.Manager import Manager

from Foundation.DatabaseManager import DatabaseManager

class RollingBallsManager(object):
    s_games = {}

    class RollingBallsSlot(object):
        def __init__(self, slotId, ballType):
            self.slotId = slotId
            self.ballType = ballType

    class RollingBallsSegment(object):
        def __init__(self):
            self.idInRoll = -1
            self.slots = []

        def appendSlots(self, slot):
            self.slots.append(slot)

    class RollingBallsRoll(object):
        def __init__(self):
            # self.id = -1
            self.segments = []

        def appendSegments(self, segment):
            self.segments.append(segment)

    class RollingBallsGame(object):
        def __init__(self, segments, rolls, rules, balls):
            self.segments = segments
            self.rolls = rolls
            self.rules = rules
            self.balls = balls

    @staticmethod
    def _onInitialize():
        return True

    @staticmethod
    def _onFinalize():
        RollingBallsManager.s_games = {}
        pass

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            Name = record.get("Name")
            SegmentsParam = record.get("Segments")
            RollsParam = record.get("Rolls")
            RulesParam = record.get("Rules")
            BallsParam = record.get("Balls")

            RollingBallsManager.loadGame(Name, module, SegmentsParam, RollsParam, RulesParam, BallsParam)

    @staticmethod
    def loadGame(name, module, SegmentsParam, RollsParam, RulesParam, BallsParam):
        segments = RollingBallsManager.loadGameSegments(module, SegmentsParam)
        rolls = RollingBallsManager.loadGameRolls(module, RollsParam, segments)
        rules = RollingBallsManager.loadGameRules(module, RulesParam, segments)
        balls = RollingBallsManager.loadGameBalls(module, BallsParam)

        game = RollingBallsManager.RollingBallsGame(segments, rolls, rules, balls)

        RollingBallsManager.s_games[name] = game
        return game

    @staticmethod
    def loadGameSegments(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        segments = {}
        for record in records:
            SegmentId = record.get("Segment")
            BallId = record.get("BallType")
            SlotId = record.get("Slot")

            if SegmentId not in segments.keys():
                segment = RollingBallsManager.RollingBallsSegment()
                segments[SegmentId] = segment
            else:
                segment = segments[SegmentId]

            slot = RollingBallsManager.RollingBallsSlot(SlotId, BallId)
            segment.appendSlots(slot)

        return segments

    @staticmethod
    def loadGameRolls(module, param, segments):
        records = DatabaseManager.getDatabaseRecords(module, param)

        rolls = {}
        for record in records:
            RollId = record.get("Roll")

            SegmentId = record.get("Segment")
            if RollId not in rolls.keys():
                roll = RollingBallsManager.RollingBallsRoll()
                rolls[RollId] = roll
            else:
                roll = rolls[RollId]

            segment = segments[SegmentId]
            roll.appendSegments(segment)
            pass

        return rolls

    @staticmethod
    def loadGameRules(module, param, segments):
        records = DatabaseManager.getDatabaseRecords(module, param)

        rules = {}
        for record in records:
            BallType = record.get("BallType")
            SegmentId = record.get("Segment")

            segment = segments[SegmentId]
            rules.setdefault(BallType, []).append(segment)

        return rules

    @staticmethod
    def loadGameBalls(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        balls = {}
        for record in records:
            BallType = record.get("BallType")
            GeneratorName = record.get("GeneratorName")

            balls[BallType] = dict(GeneratorName=GeneratorName)

        return balls

    @staticmethod
    def getGame(name):
        if name not in RollingBallsManager.s_games:
            Trace.log("Manager", 0, "RollingBallsManager.getGame: not found game %s" % (name))
            return None

        game = RollingBallsManager.s_games[name]

        return game

    @staticmethod
    def hasGame(name):
        return name in RollingBallsManager.s_games
