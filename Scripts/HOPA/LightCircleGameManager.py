from Foundation.Manager import Manager

from Foundation.DatabaseManager import DatabaseManager


class LightCircleGameManager(Manager):
    Games = {}

    class ReflectorData(object):
        def __init__(self, CircleID, ReflectorID, ReflectorPlusCount, ReflectorMinusCount, ReflectorNeedForWin, ReflectorMinusRange):
            self.CircleID = CircleID
            self.ReflectorID = ReflectorID
            self.ReflectorPlusCount = ReflectorPlusCount
            self.ReflectorMinusCount = ReflectorMinusCount
            self.ReflectorNeedForWin = ReflectorNeedForWin
            self.ReflectorMinusRange = ReflectorMinusRange

    class CircleData(object):
        def __init__(self, Game, CircleID):
            self.Game = Game
            self.CircleID = CircleID
            self.Reflectors = {}

        def addReflector(self, ref):
            if (ref.ReflectorID in self.Reflectors):
                Trace.log("Manager", 0, "LightCircleGameManager Can't add Reflector in Circle %d with id %d reflector already in" % (ref.CircleID, ref.ReflectorID))
                return

            self.Reflectors[ref.ReflectorID] = ref

    class GameData(object):
        def __init__(self, Name, UseDiagonal, CirclesNumber, CirclesRotatable, ReflectorNumber, CirclesStartAngle):
            self.Name = Name
            self.UseDiagonal = UseDiagonal
            self.CirclesNumber = CirclesNumber
            self.CirclesRotatable = CirclesRotatable
            self.ReflectorNumber = ReflectorNumber
            self.CirclesStartAngle = CirclesStartAngle
            self.Circles = {}
            for i in range(CirclesNumber):
                circle = LightCircleGameManager.CircleData(self, i)
                self.Circles[i] = circle

        def addCircleReflectors(self, CircleID, ReflectorID, ReflectorPlusCount, ReflectorMinusCount,
                                ReflectorNeedForWin, ReflectorMinusRange):
            circle = self.Circles[CircleID]
            if (circle is None):
                Trace.log("Manager", 0, "LightCircleGameManager Can't add Circle with id %d out from Game CirclesNumber" % (CircleID))
                return
            ref = LightCircleGameManager.ReflectorData(CircleID, ReflectorID, ReflectorPlusCount, ReflectorMinusCount,
                                                       ReflectorNeedForWin, ReflectorMinusRange)
            circle.addReflector(ref)

        def getPlus(self, CircleId, ReflId):
            ref = self.getRef(CircleId, ReflId)
            plus = ref.ReflectorPlusCount
            return plus
            pass

        def getMinus(self, CircleId, ReflId):
            ref = self.getRef(CircleId, ReflId)
            mines = ref.ReflectorMinusCount
            return mines
            pass

        def checkNeedForWin(self, CircleId, ReflId):
            ref = self.getRef(CircleId, ReflId)
            needForWin = ref.ReflectorNeedForWin
            return needForWin
            pass

        def getReflectorMinusRange(self, CircleId, ReflId):
            ref = self.getRef(CircleId, ReflId)
            ReflectorMinusRange = ref.ReflectorMinusRange
            return ReflectorMinusRange
            pass

        def getRef(self, CircleId, ReflId):
            circle = self.Circles[CircleId]
            reflectors = circle.Reflectors
            ref = reflectors[ReflId]
            return ref

    @staticmethod
    def _onFinalize():
        LightCircleGameManager.Games = {}
        pass

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            Name = record.get("Name")
            if Name is None or Name[0] == "#":
                continue

            if LightCircleGameManager.hasGame(Name) is True:
                Trace.log("Manager", 0, "LightCircleGameManager.loadGames game wtih name Already Loadet: %s" % Name)
                continue

            ##################################
            UseDiagonal = record.get("UseDiagonal")
            if (int(UseDiagonal) == 1):
                UseDiagonal = True
            else:
                UseDiagonal = False
            #################################
            CirclesNumber = record.get("CirclesNumber")
            CirclesNumber = int(CirclesNumber)
            ##################################
            CirclesRotatable = record.get("CirclesRotatable")
            CirclesRotatable = CirclesRotatable.split(',')
            for id, str in enumerate(CirclesRotatable):
                if (int(str) == 1):
                    CirclesRotatable[id] = True
                else:
                    CirclesRotatable[id] = False
            #################################
            ReflectorNumber = record.get("ReflectorNumber")
            ReflectorNumber = ReflectorNumber.split(',')
            for id, intt in enumerate(ReflectorNumber):
                ReflectorNumber[id] = int(intt)
            ##################################
            CirclesStartAngle = record.get("CirclesStartAngle")
            CirclesStartAngle = CirclesStartAngle.split(',')
            for id, flo in enumerate(CirclesStartAngle):
                CirclesStartAngle[id] = int(flo)
            ##################################
            Game = LightCircleGameManager.GameData(Name, UseDiagonal, CirclesNumber, CirclesRotatable,
                                                   ReflectorNumber, CirclesStartAngle)
            LightCircleGameManager.Games[Name] = Game
            LightCircleGameManager.__loadGame(Name, Game)

        return True

    @staticmethod
    def __loadGame(param, Game):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            CircleID = record.get("CircleID")
            if CircleID is None:
                continue
            CircleID = int(CircleID)

            ReflectorID = record.get("ReflectorID")
            ReflectorID = int(ReflectorID)

            ReflectorPlusCount = record.get("ReflectorPlusCount")
            ReflectorPlusCount = int(ReflectorPlusCount)

            ReflectorMinusCount = record.get("ReflectorMinusCount")
            ReflectorMinusCount = int(ReflectorMinusCount)

            ReflectorNeedForWin = record.get("ReflectorNeedForWin")
            if (int(ReflectorNeedForWin) == 1):
                ReflectorNeedForWin = True
            else:
                ReflectorNeedForWin = False

            ReflectorMinusRange = record.get("ReflectorMinusRange")
            ReflectorMinusRange = int(ReflectorMinusRange)

            Game.addCircleReflectors(CircleID, ReflectorID, ReflectorPlusCount, ReflectorMinusCount,
                                     ReflectorNeedForWin, ReflectorMinusRange)

        return True
        pass

    @staticmethod
    def hasGame(name):
        return name in LightCircleGameManager.Games
        pass

    @staticmethod
    def getGame(name):
        if (LightCircleGameManager.hasGame(name) is False):
            Trace.log("Manager", 0, "LightCircleGameManager.getGame can't find game with Name: %s" % name)
            return None
        return LightCircleGameManager.Games[name]
