from Foundation.DatabaseManager import DatabaseManager

class PlanetGameManager(object):
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
            pass

        def getStartTiming(self):
            return self.startTiming
            pass

        def getWinTiming(self):
            return self.winTiming
            pass

        def getDuration(self):
            return self.duration
            pass

        def getAccuracy(self):
            return self.accuracy
            pass

        pass

    @staticmethod
    def onFinalize():
        PlanetGameManager.s_objects = {}
        pass

    @staticmethod
    def loadParams(module, params):
        records = DatabaseManager.getDatabaseRecords(module, params)

        for values in records:
            enigmaName = values.get("Name")
            collectionParam = values.get("Collection")
            PlanetGameManager.loadPlanetGameCollection(enigmaName, module, collectionParam)
            pass
        pass

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
            pass

        PlanetGameManager.s_objects[enigmaName] = planetList
        pass

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
        pass

    pass

pass