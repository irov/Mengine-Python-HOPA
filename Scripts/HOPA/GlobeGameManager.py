from Foundation.DatabaseManager import DatabaseManager

class GlobeGameManager(object):
    Games = {}

    class GameData(object):
        def __init__(self, Name, LvlStart, LvlWin):
            self.Name = Name
            self.LvlStart = LvlStart
            self.LvlWin = LvlWin
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

            if (GlobeGameManager.hasGame(Name) is True):
                Trace.log("Manager", 0, "GlobeGameManager.loadGames game wtih name Already Loadet: %s" % (Name))
                continue
                pass
            ##################################
            LvlStart = record.get("LvlStart")
            LvlWin = record.get("LvlWin")
            #################################
            LvlStartData = []
            LvlWinData = []

            LvlStart = LvlStart.split(';')
            LvlWin = LvlWin.split(';')

            for id in range(len(LvlStart)):
                LvlStartData.append([])
                LvlWinData.append([])
                LvlStartVV = LvlStart[id].split(',')
                LvlWinVV = LvlWin[id].split(',')
                for i in range(len(LvlStartVV)):
                    LvlStartData[id].append(int(LvlStartVV[i]))
                    LvlWinData[id].append(int(LvlWinVV[i]))
                    pass

                pass

            Game = GlobeGameManager.GameData(Name, LvlStartData, LvlWinData)
            GlobeGameManager.Games[Name] = Game
            pass

        return True
        pass

    @staticmethod
    def hasGame(name):
        return name in GlobeGameManager.Games
        pass

    @staticmethod
    def getGame(name):
        if (GlobeGameManager.hasGame(name) is False):
            Trace.log("Manager", 0, "GlobeGameManager.getGame can't find game with Name: %s" % (name))
            return None
            pass
        return GlobeGameManager.Games[name]
        pass

    pass