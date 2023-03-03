from Foundation.DatabaseManager import DatabaseManager


class RailRoadGameManager(object):
    Games = {}

    class MovieData(object):
        def __init__(self, From, Midl, To, Movie):
            self.From = From
            self.Midl = Midl
            self.To = To
            self.Movie = Movie

    class IntersectData(object):
        def __init__(self, Id, From, To, MovieIdle, MovieRotate, MovieUnderMouse, Slot, Win):
            self.Id = Id
            self.From = From
            self.To = To
            self.MovieIdle = MovieIdle
            self.MovieRotate = MovieRotate
            self.MovieUnderMouse = MovieUnderMouse
            self.Slot = Slot
            self.Win = Win

    class GameData(object):
        def __init__(self, Name):
            self.Name = Name
            self.Movies = []
            self.Intersect = {}

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            Name = record.get("Name")
            if Name is None or Name[0] == "#":
                continue

            if RailRoadGameManager.hasGame(Name) is True:
                Trace.log("Manager", 0, "RailRoadGameManager.loadGames game wtih name Already Loadet: %s" % Name)
                continue
            ##################################
            MovieData = record.get("ParamMovies")
            IntersectData = record.get("ParamIntersection")

            Game = RailRoadGameManager.GameData(Name)
            RailRoadGameManager.Games[Name] = Game

            RailRoadGameManager.loadGamesMovie(Game, module, MovieData)
            RailRoadGameManager.loadGamesIntersect(Game, module, IntersectData)

        return True

    @staticmethod
    def loadGamesMovie(Game, module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            From = record.get("From")
            if From is None:
                continue
            Midl = record.get("Midl")
            To = record.get("To")
            Movie = record.get("Movie")
            moc = RailRoadGameManager.MovieData(From, Midl, To, Movie)
            Game.Movies.append(moc)

    @staticmethod
    def loadGamesIntersect(Game, module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            Id = record.get("Id")
            if Id is None:
                continue

            From = record.get("From")
            To = record.get("To")
            MovieIdle = record.get("MovieIdle")
            MovieRotate = record.get("MovieRotate")
            MovieUnderMouse = record.get("MovieUnderMouse")
            Slot = record.get("Slot")
            Win = record.get("Win", None)
            if (Win == "Win"):
                Win = True
            else:
                Win = False

            interrr = RailRoadGameManager.IntersectData(Id, From, To, MovieIdle, MovieRotate, MovieUnderMouse, Slot, Win)
            if Id not in Game.Intersect:
                intAer = []
                Game.Intersect[Id] = intAer
            else:
                intAer = Game.Intersect[Id]
            intAer.append(interrr)

    @staticmethod
    def hasGame(name):
        return name in RailRoadGameManager.Games

    @staticmethod
    def getGame(name):
        if (RailRoadGameManager.hasGame(name) is False):
            Trace.log("Manager", 0, "RailRoadGameManager.getGame can't find game with Name %s" % name)
            return None
        return RailRoadGameManager.Games[name]
