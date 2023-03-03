from Foundation.DatabaseManager import DatabaseManager


class PetnaGameManager(object):
    Games = {}

    class GameData(object):
        def __init__(self, Name, FieldWidth, FieldHeight, StartData):
            self.Name = Name
            self.FieldWidth = FieldWidth
            self.FieldHeight = FieldHeight
            self.StartData = StartData

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            Name = record.get("Name")
            if Name is None or Name[0] == "#":
                continue
                pass

            if (PetnaGameManager.hasGame(Name) is True):
                Trace.log("Manager", 0, "PetnaGameManager.loadGames game wtih name Already Loadet: %s" % Name)
                continue
                pass
            ##################################
            FieldWidth = record.get("FieldWidth")
            FieldWidth = int(FieldWidth)
            FieldHeight = record.get("FieldHeight")
            FieldHeight = int(FieldHeight)
            StartData = record.get("StartData")
            #################################
            LvlStartData = []

            LvlStart = StartData.split(';')

            for id in range(len(LvlStart)):
                LvlStartData.append([])
                LvlStartX = LvlStart[id].split(',')
                for i in range(len(LvlStartX)):
                    LvlStartData[id].append(int(LvlStartX[i]))
                    pass
                pass

            Game = PetnaGameManager.GameData(Name, FieldWidth, FieldHeight, LvlStartData)
            PetnaGameManager.Games[Name] = Game
            pass

        return True

    @staticmethod
    def hasGame(name):
        return name in PetnaGameManager.Games

    @staticmethod
    def getGame(name):
        if (PetnaGameManager.hasGame(name) is False):
            Trace.log("Manager", 0, "PetnaGameManager.getGame can't find game with Name %s" % name)
            return None
            pass
        return PetnaGameManager.Games[name]
