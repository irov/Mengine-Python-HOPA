from Foundation.Manager import Manager

from Foundation.DatabaseManager import DatabaseManager
from Foundation.DemonManager import DemonManager

class ReagentsManager(Manager):
    s_reagentItems = {}
    s_reagentMixes = {}
    s_reagentAddMovies = {}
    s_maxAdd = None

    class ReagentsEnigma(object):
        def __init__(self, winMovieName, looseMovieName, items):
            self.winMovieName = winMovieName
            self.looseMovieName = looseMovieName
            self.items = items
            pass

        def getWinMovieName(self):
            return self.winMovieName

        def getLooseMovieName(self):
            return self.looseMovieName

        def getItems(self):
            return self.items

    @staticmethod
    def _onFinalize():
        ReagentsManager.s_reagentItems = {}
        ReagentsManager.s_reagentMixes = {}
        ReagentsManager.s_reagentAddMovies = {}
        ReagentsManager.s_maxAdd = None
        pass

    @staticmethod
    def loadParams(module, param):
        if param == "Reagents":
            ReagentsManager.loadReagents(module, "Reagents")
            pass
        if param == "ReagentsMixes":
            ReagentsManager.loadReagentMixes(module, "ReagentsMixes")
            pass
        pass

    @staticmethod
    def loadReagents(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)
        for record in records:
            itemsParam = record.get("ItemsParam")
            addMoviesParam = record.get("AddMoviesParam")
            maxAdd = record.get("MaxAdd", 0)

            ReagentsManager.loadReagentItems(module, itemsParam)
            ReagentsManager.loadAddMovies(module, addMoviesParam)
            ReagentsManager.s_maxAdd = maxAdd
            pass
        pass

    @staticmethod
    def loadReagentItems(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)
        for record in records:
            name = record.get("Name")
            itemObjectName = record.get("ItemObjectName")

            entityObject = DemonManager.getDemon("Reagents")
            itemObject = entityObject.getObject(itemObjectName)

            ReagentsManager.s_reagentItems[name] = itemObject
            pass
        pass

    @staticmethod
    def loadAddMovies(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)
        for record in records:
            id = record.get("ID")
            MovieName = record.get("MovieName")

            if id not in ReagentsManager.s_reagentAddMovies:
                ReagentsManager.s_reagentAddMovies[id] = []
                pass

            entityObject = DemonManager.getDemon("Reagents")
            movieObject = entityObject.getObject(MovieName)
            ReagentsManager.s_reagentAddMovies[id].append(movieObject)
            pass
        pass

    @staticmethod
    def loadReagentMixes(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)
        for record in records:
            name = record.get("EnigmaName")
            mixParam = record.get("MixParam")
            winMovieName = record.get("WinMovieName")
            looseMovieName = record.get("LooseMovieName")

            items = ReagentsManager.loadMixItems(module, mixParam)
            reagentMix = ReagentsManager.ReagentsEnigma(winMovieName, looseMovieName, items)
            ReagentsManager.s_reagentMixes[name] = reagentMix
            pass
        pass

    @staticmethod
    def loadMixItems(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)
        items = []
        for record in records:
            name = record.get("Name")

            items.append(name)
            pass
        return items
        pass

    @staticmethod
    def getReagents():
        return ReagentsManager.s_reagentItems
        pass

    @staticmethod
    def getAddMovies():
        return ReagentsManager.s_reagentAddMovies
        pass

    @staticmethod
    def getMaxAdd():
        return ReagentsManager.s_maxAdd
        pass

    @staticmethod
    def hasReagent(name):
        if name not in ReagentsManager.s_reagentItems:
            return False
            pass

        return True
        pass

    @staticmethod
    def getReagentsMix(name):
        if name is None:
            return None
            pass
        return ReagentsManager.s_reagentMixes[name]
        pass

    @staticmethod
    def hasReagentsMix(name):
        if name not in ReagentsManager.s_reagentMixes:
            return False
            pass

        return True
        pass

    pass
