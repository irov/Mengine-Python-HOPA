from Foundation.DatabaseManager import DatabaseManager


class PaperConnectGameManager(object):
    Games = {}

    class Paper(object):
        def __init__(self, movie, moving):
            self.PaperMovieName = movie
            self.Moving = moving
            self.ConectTo = {}

        def addConnect(self, paper):
            self.ConectTo[paper.PaperMovieName] = paper

    class GameData(object):
        def __init__(self, Name):
            self.Name = Name
            self.Parts = {}

    @staticmethod
    def loadGames(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            Name = record.get("Name")
            if Name is None or Name[0] == "#":
                continue
                pass
            PartFileName = record.get("PartFileName")
            ConnectsFileName = record.get("ConnectsFileName")

            if (PaperConnectGameManager.hasGame(Name) is True):
                Trace.log("Manager", 0, "PaperConnectGameManager.loadGames game wtih name Already Loadet :", Name)
                continue
                pass

            Game = PaperConnectGameManager.GameData(Name)
            PaperConnectGameManager.Games[Name] = Game
            PaperConnectGameManager.__loadGameParts(module, PartFileName, Game)
            PaperConnectGameManager.__loadGameConnects(module, ConnectsFileName, Game)
            pass

        return True
        pass

    @staticmethod
    def __loadGameParts(module, param, Game):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            PartName = record.get("PartName")
            if PartName is None or PartName[0] == "#":
                continue
                pass

            CanMove = record.get("CanMove")
            if (CanMove == "Yes"):
                CanMove = True
                pass
            else:
                CanMove = False
                pass

            paper = PaperConnectGameManager.Paper(PartName, CanMove)
            Game.Parts[PartName] = paper
            pass

        return True
        pass

    @staticmethod
    def __loadGameConnects(module, param, Game):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            FromPoint = record.get("FromPoint")
            if FromPoint is None or FromPoint[0] == "#":
                continue
                pass

            ToPoint = record.get("ToPoint")

            fromObj = Game.Parts[FromPoint]
            toObj = Game.Parts[ToPoint]

            fromObj.addConnect(toObj)
            toObj.addConnect(fromObj)
            pass

        return True
        pass

    @staticmethod
    def hasGame(name):
        return name in PaperConnectGameManager.Games
        pass

    @staticmethod
    def getGame(name):
        if (PaperConnectGameManager.hasGame(name) is False):
            Trace.log("Manager", 0, "PaperConnectGameManager.getGame can't find game with Name ", name)
            return None
            pass
        return PaperConnectGameManager.Games[name]
