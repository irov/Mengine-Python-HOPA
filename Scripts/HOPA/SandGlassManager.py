from Foundation.Manager import Manager

from Foundation.DatabaseManager import DatabaseManager

class SandGlassManager(Manager):
    Games = {}

    class Connect_Data(object):
        def __init__(self, Id_From, Id_To, Movie_Idle, Movie_Use, Movie_Select):
            self.Id_From = int(Id_From)
            self.Id_To = int(Id_To)
            self.Movie_Idle = Movie_Idle
            self.Movie_Use = Movie_Use
            self.Movie_Select = Movie_Select
            pass

        def __str__(self):
            return "%s %s" % (self.Id_From, self.Id_To)

        def __repr__(self):
            return "%s %s" % (self.Id_From, self.Id_To)

    class Point_Data(object):
        def __init__(self, Id, Socket_Name, Movie_Idle_Active, Movie_Idle_Passive, Movie_Use, Movie_Select):
            self.Id = int(Id)
            self.Socket_Name = Socket_Name
            self.Movie_Idle_Active = Movie_Idle_Active
            self.Movie_Idle_Passive = Movie_Idle_Passive
            self.Movie_Use = Movie_Use
            self.Movie_Select = Movie_Select

        def __str__(self):
            return "%s" % (self.Id)

        def __repr__(self):
            return "%s" % (self.Id)

    class Game_Data(object):
        def __init__(self, Name):
            self.Name = Name
            self.Points = []
            self.Connects = []

    @staticmethod
    def _onFinalize():
        SandGlassManager.Games = {}
        pass

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            Name = record.get("Name")
            if Name is None or Name[0] == "#":
                continue

            if (SandGlassManager.hasGame(Name) is True):
                Trace.log("Manager", 0, "SandGlassManager.loadGames game wtih name Already Loadet: %s" % Name)
                continue
            ##################################
            Point_Data = record.get("Point_Data")
            Connect_Data = record.get("Connect_Data")

            Game = SandGlassManager.Game_Data(Name)
            SandGlassManager.Games[Name] = Game

            SandGlassManager.loadGamesPoint(Game, module, Point_Data)
            SandGlassManager.loadGamesConnect(Game, module, Connect_Data)
            pass

        return True
        pass

    @staticmethod
    def loadGamesPoint(Game, module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            Id = record.get("Id")
            if Id is None:
                continue

            Socket_Name = record.get("Socket_Name")
            Movie_Idle_Active = record.get("Movie_Idle_Active")
            Movie_Idle_Passive = record.get("Movie_Idle_Passive")
            Movie_Use = record.get("Movie_Use")
            Movie_Select = record.get("Movie_Select")
            path = SandGlassManager.Point_Data(Id, Socket_Name, Movie_Idle_Active, Movie_Idle_Passive, Movie_Use,Movie_Select)
            Game.Points.append(path)

    @staticmethod
    def loadGamesConnect(Game, module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            Id_From = record.get("Id_From")
            if Id_From is None:
                continue
            Id_To = record.get("Id_To")
            Movie_Idle = record.get("Movie_Idle")
            Movie_Use = record.get("Movie_Use")
            Movie_Select = record.get("Movie_Select")

            path = SandGlassManager.Connect_Data(Id_From, Id_To, Movie_Idle, Movie_Use, Movie_Select)
            Game.Connects.append(path)

    @staticmethod
    def hasGame(name):
        return name in SandGlassManager.Games
        pass

    @staticmethod
    def getGame(name):
        if (SandGlassManager.hasGame(name) is False):
            Trace.log("Manager", 0, "SandGlassManager.getGame can't find game with Name %s" % name)
            return None
        return SandGlassManager.Games[name]
