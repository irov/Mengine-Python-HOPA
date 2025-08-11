from Foundation.Manager import Manager

from Foundation.DatabaseManager import DatabaseManager

class PlanetGameManager(Manager):
    s_objects = {}

    class Planet(object):
        def __init__(self, duration, movieLeftName, startTiming, winTiming, accuracy):
            self.duration = duration
            self.movieName = movieLeftName
            self.startTiming = startTiming
            self.winTiming = winTiming
            self.accuracy = accuracy
            pass

        def getMovieName(self):
            return self.movieName

        def getStartTiming(self):
            return self.startTiming

        def getWinTiming(self):
            return self.winTiming

        def getDuration(self):
            return self.duration

        def getAccuracy(self):
            return self.accuracy

    @staticmethod
    def _onFinalize():
        PlanetGameManager.s_objects = {}
        pass

    @staticmethod
    def loadParams(module, params):
        records = DatabaseManager.getDatabaseRecords(module, params)

        for values in records:
            enigmaName = values.get("Name")
            collectionParam = values.get("Collection")
            PlanetGameManager.loadPlanetGameCollection(enigmaName, module, collectionParam)

    @staticmethod
    def loadPlanetGameCollection(enigmaName, module, collectionParam):
        records = DatabaseManager.getDatabaseRecords(module, collectionParam)

        planetList = []
        for values in records:
            MovieName = values.get("MovieName")
            Duration = values.get("Duration")
            StartTiming = values.get("StartTiming")
            WinTiming = values.get("WinTiming")
            Accuracy = values.get("Accuracy")
            planet = PlanetGameManager.Planet(Duration, MovieName, StartTiming, WinTiming, Accuracy)
            planetList.append(planet)

        PlanetGameManager.s_objects[enigmaName] = planetList

    @staticmethod
    def getPlanetGame(name):
        if PlanetGameManager.hasPlanetGame(name) is False:
            return None
            pass
        record = PlanetGameManager.s_objects[name]
        return record
        pass

    @staticmethod
    def hasPlanetGame(name):
        if name not in PlanetGameManager.s_objects:
            Trace.log("PlanetGameManager", 0, "PlanetGameManager.hasPlanetGame: : invalid param")
            return False
            pass
        return True
