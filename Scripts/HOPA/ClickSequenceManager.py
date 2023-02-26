from Foundation.DatabaseManager import DatabaseManager

class ClickSequenceManager(object):
    Games = {}

    class Sequence(object):
        def __init__(self, Socket, Socket_Movie):
            self.Socket = Socket
            self.Socket_Movie = Socket_Movie
            pass
        pass

    class Cliker(object):
        def __init__(self, Socket, Socket_Movie, Movie_Play):
            self.Socket = Socket
            self.Socket_Movie = Socket_Movie
            self.Movie_Play = Movie_Play
            pass
        pass

    class GameData(object):
        def __init__(self, Name):
            self.Name = Name
            self.Sequences = []
            self.Clikers = []
            pass

        def add_Seq(self, Seq):
            self.Sequences.append(Seq)
            pass

        def add_Click(self, click):
            self.Clikers.append(click)
            pass
        pass

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            Name = record.get("Name")

            if Name is None or Name[0] == "#":
                continue
                pass

            if (ClickSequenceManager.hasGame(Name) is True):
                Trace.log("Manager", 0, "ClickSequenceManager.loadGames game wtih name Already Loadet: %s", Name)
                continue
                pass

            Game = ClickSequenceManager.GameData(Name)
            ClickSequenceManager.Games[Name] = Game
            ##################################
            GameSequences = record.get("GameSequences")
            GameClikers = record.get("GameClikers")
            #################################
            ClickSequenceManager.loadGame_Seq(module, GameSequences, Game)
            ClickSequenceManager.loadGame_Click(module, GameClikers, Game)
            pass

        return True
        pass

    @staticmethod
    def loadGame_Seq(module, param, Game):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            Socket = record.get("Socket")
            if Socket is None or Socket[0] == "#":
                continue
                pass

            Socket_Movie = record.get("Socket_Movie")

            Seq = ClickSequenceManager.Sequence(Socket, Socket_Movie)
            Game.add_Seq(Seq)
            pass
        pass

    @staticmethod
    def loadGame_Click(module, param, Game):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            Socket = record.get("Socket")
            if Socket is None or Socket[0] == "#":
                continue
                pass

            Socket_Movie = record.get("Socket_Movie")
            Movie_Play = record.get("Movie_Play")

            cliker = ClickSequenceManager.Cliker(Socket, Socket_Movie, Movie_Play)
            Game.add_Click(cliker)
            pass
        pass

    @staticmethod
    def hasGame(name):
        return name in ClickSequenceManager.Games
        pass

    @staticmethod
    def getGame(name):
        if (ClickSequenceManager.hasGame(name) is False):
            Trace.log("Manager", 0, "ClickSequenceManager.getGame can't find game with Name: %s" % (name))
            return None
            pass
        return ClickSequenceManager.Games[name]
        pass

    pass