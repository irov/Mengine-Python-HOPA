from Foundation.DatabaseManager import DatabaseManager

class FragmentsRollManager(object):
    s_games = {}

    class FragmentsRollGame(object):
        def __init__(self, fragments, cells, rules):
            self.fragments = fragments
            self.cells = cells
            self.rules = rules
            pass
        pass

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            Name = record.get("Name")
            CellsParam = record.get("Cells")
            RulesParam = record.get("Rules")
            FragmentsParam = record.get("Fragments")

            FragmentsRollManager.loadGame(Name, module, FragmentsParam, CellsParam, RulesParam)
            pass

        return True
        pass

    @staticmethod
    def loadGame(name, module, FragmentsParam, CellsParam, RulesParam):
        fragments = FragmentsRollManager.loadGameFragments(module, FragmentsParam)
        cells = FragmentsRollManager.loadGameCells(module, CellsParam)
        rules = FragmentsRollManager.loadGameRules(module, RulesParam)

        game = FragmentsRollManager.FragmentsRollGame(fragments, cells, rules)
        FragmentsRollManager.s_games[name] = game
        pass

    @staticmethod
    def loadGameFragments(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)
        fragments = {}
        for record in records:
            fragmentId = record.get("FragmentId")
            objectName = record.get("ObjectName")
            X = record.get("X")
            Y = record.get("Y")
            fragments[fragmentId] = dict(ObjectName=objectName, X=X, Y=Y)
            pass
        return fragments
        pass

    @staticmethod
    def loadGameCells(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)
        cells = []
        for record in records:
            X = record.get("X")
            Y = record.get("Y")
            MovieSlotName = record.get("MovieSlotName")

            cells.append(dict(X=X, Y=Y, MovieSlotName=MovieSlotName))
            pass
        return cells
        pass

    @staticmethod
    def loadGameRules(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)
        rules = {}
        for record in records:
            X = record.get("X")
            Y = record.get("Y")
            FragmentId = record.get("FragmentId")
            rules[FragmentId] = dict(X=X, Y=Y)
            pass
        return rules
        pass

    @staticmethod
    def getGame(name):
        if name not in FragmentsRollManager.s_games:
            Trace.log("Manager", 0, "FragmentsRollManager.getGame: not found game %s" % (name))
            return None
            pass
        game = FragmentsRollManager.s_games[name]
        return game
        pass

    @staticmethod
    def hasGame(name):
        return name in FragmentsRollManager.s_games
        pass

    pass