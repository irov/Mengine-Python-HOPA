from Foundation.Manager import Manager

from Foundation.DatabaseManager import DatabaseManager

class ConnectLampManager(Manager):
    Games = {}

    class Connect_Data(object):
        def __init__(self, Id_From, Id_To, Movie_Idle, Movie_Select):
            self.Id_From = int(Id_From)
            self.Id_To = int(Id_To)
            self.Movie_Idle = Movie_Idle
            self.Movie_Select = Movie_Select
            pass

        def __str__(self):
            return "%s %s" % (self.Id_From, self.Id_To)

        def __repr__(self):
            return "%s %s" % (self.Id_From, self.Id_To)

    class Point_Data(object):
        def __init__(self, Id, Connect_Number, Movie_Idle_Active, Movie_Idle_Passive):
            self.Id = int(Id)
            self.Connect_Number = int(Connect_Number)
            self.Movie_Idle_Active = Movie_Idle_Active
            self.Movie_Idle_Passive = Movie_Idle_Passive

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
        ConnectLampManager.Games = {}
        pass

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            Name = record.get("Name")
            if Name is None or Name[0] == "#":
                continue

            if (ConnectLampManager.hasGame(Name) is True):
                Trace.log("Manager", 0, "ConnectLampManager.loadGames game wtih name Already Loadet : %s" % (Name))
                continue
            ##################################
            Point_Data = record.get("Point_Data")
            Connect_Data = record.get("Connect_Data")

            Game = ConnectLampManager.Game_Data(Name)
            ConnectLampManager.Games[Name] = Game

            ConnectLampManager.loadGamesPoint(module, Game, Point_Data)
            ConnectLampManager.loadGamesConnect(module, Game, Connect_Data)

        return True

    @staticmethod
    def loadGamesPoint(module, Game, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            Id = record.get("Id")
            if Id is None:
                continue
                pass

            Connect_Number = record.get("Connect_Number")
            Movie_Idle_Active = record.get("Movie_Idle_Active")
            Movie_Idle_Passive = record.get("Movie_Idle_Passive")
            path = ConnectLampManager.Point_Data(Id, Connect_Number, Movie_Idle_Active, Movie_Idle_Passive)
            Game.Points.append(path)
            pass
        pass

    @staticmethod
    def loadGamesConnect(module, Game, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            Id_From = record.get("Id_From")
            if Id_From is None:
                continue
                pass
            Id_To = record.get("Id_To")
            Movie_Idle = record.get("Movie_Idle")
            Movie_Select = record.get("Movie_Select")

            path = ConnectLampManager.Connect_Data(Id_From, Id_To, Movie_Idle, Movie_Select)
            Game.Connects.append(path)
            pass
        pass

    @staticmethod
    def hasGame(name):
        return name in ConnectLampManager.Games

    @staticmethod
    def getGame(name):
        if (ConnectLampManager.hasGame(name) is False):
            Trace.log("Manager", 0, "ConnectLampManager.getGame can't find game with Name: %s" % (name))
            return None
        return ConnectLampManager.Games[name]
