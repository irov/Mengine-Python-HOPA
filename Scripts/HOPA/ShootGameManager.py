from Foundation.DatabaseManager import DatabaseManager


class ShootGameManager(object):
    Games = {}

    class PathData(object):
        def __init__(self, Movie, TimeShotDec, PathLen):
            self.Movie = Movie
            self.TimeShotDec = TimeShotDec
            self.PathLen = PathLen

    class Game_Data(object):
        def __init__(self, Name, ShootCount, ShootWin):
            self.Name = Name
            self.ShootCount = int(ShootCount)
            self.ShootWin = int(ShootWin)
            self.Pathes = []

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            Name = record.get("Name")
            if Name is None or Name[0] == "#":
                continue
                pass

            if (ShootGameManager.hasGame(Name) is True):
                Trace.log("Manager", 0, "ShooGameManager.loadGames game wtih name Already Loadet: %s" % Name)
                continue
                pass
            ##################################
            GameData = record.get("GameData")

            ShootCount = record.get("ShootCount")
            ShootWin = record.get("ShootWin")

            Game = ShootGameManager.Game_Data(Name, ShootCount, ShootWin)
            ShootGameManager.Games[Name] = Game

            ShootGameManager.loadGamesPath(Game, module, GameData)
            pass

        return True
        pass

    @staticmethod
    def loadGamesPath(Game, module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            Movie = record.get("Movie")
            if Movie is None or Movie[0] == "#":
                continue
                pass

            TimeShotDec = record.get("TimeShotDec", 0)
            PathLen = record.get("PathLen")
            path = ShootGameManager.PathData(Movie, TimeShotDec, PathLen)
            Game.Pathes.append(path)
            pass
        pass

    @staticmethod
    def hasGame(name):
        return name in ShootGameManager.Games
        pass

    @staticmethod
    def getGame(name):
        if (ShootGameManager.hasGame(name) is False):
            Trace.log("Manager", 0, "ShooGameManager.getGame can't find game with Name %s" % name)
            Trace.trace()
            return None
            pass
        return ShootGameManager.Games[name]
