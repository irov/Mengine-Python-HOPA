from Foundation.DatabaseManager import DatabaseManager
from Foundation.Manager import Manager


class AmazingMazeParam(object):
    def __init__(self, EnigmaName, FinishIdle, FinishReached, HeroNode, HeroIdle, HeroMove, HeroFinish, Maze,
                 HeroSpawnPoint, MoveMode, RotationSpeed, InitSpeed, MaxSpeed, Acceleration, BreakingMult,
                 TargetReachDistanceThreshold, ZeroVelocityThreshold, bUseCursorPointer, PointerPlaced, PointerReached,
                 PointerActive):
        self.EnigmaName = EnigmaName
        self.FinishIdle = FinishIdle
        self.FinishReached = FinishReached
        self.HeroNode = HeroNode
        self.HeroIdle = HeroIdle
        self.HeroMove = HeroMove
        self.HeroFinish = HeroFinish
        self.Maze = Maze
        self.HeroSpawnPoint = HeroSpawnPoint
        self.MoveMode = MoveMode
        self.RotationSpeed = RotationSpeed
        self.InitSpeed = InitSpeed
        self.MaxSpeed = MaxSpeed
        self.Acceleration = Acceleration
        self.BreakingMult = BreakingMult
        self.TargetReachDistanceThreshold = TargetReachDistanceThreshold
        self.ZeroVelocityThreshold = ZeroVelocityThreshold
        self.bUseCursorPointer = bUseCursorPointer
        self.PointerPlaced = PointerPlaced
        self.PointerReached = PointerReached
        self.PointerActive = PointerActive


class AmazingMazeManager(Manager):
    s_params = {}

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            '''
            EnigmaName	
            FinishIdle	FinishReached	
            HeroNode	HeroIdle	HeroMove	HeroFinish	
            Maze	
            HeroSpawnPoint	MoveMode	RotationSpeed	
            InitSpeed	MaxSpeed	Acceleration	BreakingMult	
            TargetReachDistanceThreshold	ZeroVelocityThreshold	
            bUseCursorPointer	PointerPlaced	PointerReached	PointerActive
            '''
            EnigmaName = record.get('EnigmaName')
            FinishIdle = record.get('FinishIdle')
            FinishReached = record.get('FinishReached')

            HeroNode = record.get('HeroNode')
            HeroIdle = record.get('HeroIdle')
            HeroMove = record.get('HeroMove')
            HeroFinish = record.get('HeroFinish')

            Maze = record.get('Maze')

            HeroSpawnPoint = record.get('HeroSpawnPoint', '0.0, 0.0')
            HeroSpawnPoint = tuple([float(i) for i in HeroSpawnPoint.split(",")])

            MoveMode = record.get('MoveMode', 1)
            RotationSpeed = record.get('RotationSpeed', 500.0)

            InitSpeed = record.get('InitSpeed', 40.0)
            MaxSpeed = record.get('MaxSpeed', 80.0)
            Acceleration = record.get('Acceleration', 500.0)
            BreakingMult = record.get('BreakingMult', 4.0)

            TargetReachDistanceThreshold = record.get('TargetReachDistanceThreshold', 15.0)
            ZeroVelocityThreshold = record.get('ZeroVelocityThreshold', 5.0)

            bUseCursorPointer = record.get('bUseCursorPointer', False)
            PointerPlaced = record.get('PointerPlaced')
            PointerReached = record.get('PointerReached')
            PointerActive = record.get('PointerActive')

            param = AmazingMazeParam(EnigmaName, FinishIdle, FinishReached, HeroNode, HeroIdle, HeroMove, HeroFinish,
                                     Maze, HeroSpawnPoint, MoveMode, RotationSpeed, InitSpeed, MaxSpeed, Acceleration,
                                     BreakingMult, TargetReachDistanceThreshold, ZeroVelocityThreshold,
                                     bUseCursorPointer, PointerPlaced, PointerReached, PointerActive)

            AmazingMazeManager.s_params[EnigmaName] = param

        return True

    @staticmethod
    def getParam(enigma_name):
        return AmazingMazeManager.s_params.get(enigma_name)
