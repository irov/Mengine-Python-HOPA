from Foundation.DatabaseManager import DatabaseManager

class ShootingRangeManager(object):
    shootingRanges = {}

    class SingleShootingRange(object):
        def __init__(self):
            self.gunMovies = []
            self.targetMovies = []
            self.isWrongTarget = []
            self.balls = []
            self.ball_sprite = []
            self.markers = []
            self.carriers = []
            self.ball_limit = 0
            pass

        def accept_fill(self):
            if self.ball_limit is None:
                Trace.log("ShootingRangeManager", 0, "ShootingRangeManager ball limit was not set!!! ")
            if len(self.balls) != len(self.gunMovies):
                Trace.log("ShootingRangeManager", 0, "ShootingRangeManager not equal number of gun and shoot movies!!! ")
            if not self.carriers or not self.ball_sprite or not self.markers:
                Trace.log("ShootingRangeManager", 0, "ShootingRangeManager not all column was filled !!! ")
            pass

        def addGunMovie(self, gunMovie):
            if gunMovie:
                self.gunMovies.append(gunMovie)
                pass

        def addTargetMovie(self, targetMovie):
            if targetMovie:
                self.targetMovies.append(targetMovie)
                pass

        def addBall(self, ball):
            if ball:
                self.balls.append(ball)
                pass

        def addBallSprite(self, sprite):
            if sprite:
                self.ball_sprite.append(sprite)
                pass

        def addMarkers(self, marker):
            if marker:
                self.markers.append(marker)
                pass

        def addCarrier(self, carrierMovie):
            if carrierMovie:
                self.carriers.append(carrierMovie)
                pass

        def setBallLimit(self, limit):
            if isinstance(limit, int):
                self.ball_limit = limit
                pass

        def getGunMovies(self):
            return self.gunMovies
            pass

        def getTargetMovies(self):
            return self.targetMovies
            pass

        def getBalls(self):
            return self.balls

        def getMarks(self):
            return self.markers

        def getBallSprite(self):
            return self.ball_sprite

        def getCarriers(self):  # change after flip feature
            return self.carriers[0]

        def getLimit(self):
            return self.ball_limit

    pass

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            name = record.get("Name")
            table_name = record.get("Table")
            ShootingRangeManager.loadRow(module, table_name, name)
            pass
        pass

    @staticmethod
    def loadRow(module, param, name):
        records = DatabaseManager.getDatabaseRecords(module, param)
        shootingRange = ShootingRangeManager.SingleShootingRange()
        for record in records:
            targetMovie = record.get("Targets")
            shootingRange.addTargetMovie(targetMovie)
            gunMovie = record.get("Guns")
            shootingRange.addGunMovie(gunMovie)
            balls = record.get("Balls")
            shootingRange.addBall(balls)
            BallSprite = record.get("BallSprite")
            shootingRange.addBallSprite(BallSprite)
            Markers = record.get("Markers")
            shootingRange.addMarkers(Markers)
            Carriers = record.get("Carriers")
            shootingRange.addCarrier(Carriers)
            BallLimit = record.get("BallLimit")
            shootingRange.setBallLimit(BallLimit)
            pass
        shootingRange.accept_fill()
        ShootingRangeManager.shootingRanges[name] = shootingRange
        pass

    @staticmethod
    def genGunMovies(EnigmaName):
        storage_entry = ShootingRangeManager.shootingRanges[EnigmaName]
        return storage_entry.getGunMovies()
        pass

    @staticmethod
    def getTargetMovie(EnigmaName):
        storage_entry = ShootingRangeManager.shootingRanges[EnigmaName]
        return storage_entry.getTargetMovies()
        pass

    @staticmethod
    def getBallsMovie(EnigmaName):
        storage_entry = ShootingRangeManager.shootingRanges[EnigmaName]
        return storage_entry.getBalls()
        pass

    @staticmethod
    def getCarriers(EnigmaName):
        storage_entry = ShootingRangeManager.shootingRanges[EnigmaName]
        return storage_entry.getCarriers()
        pass

    @staticmethod
    def getLimit(EnigmaName):
        storage_entry = ShootingRangeManager.shootingRanges[EnigmaName]
        return storage_entry.getLimit()
        pass

    @staticmethod
    def getBallSprite(EnigmaName):
        storage_entry = ShootingRangeManager.shootingRanges[EnigmaName]
        return storage_entry.getBallSprite()
        pass

    @staticmethod
    def getMarks(EnigmaName):
        storage_entry = ShootingRangeManager.shootingRanges[EnigmaName]
        return storage_entry.getMarks()
        pass