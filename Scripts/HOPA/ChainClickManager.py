from Foundation.Manager import Manager
from Foundation.DatabaseManager import DatabaseManager

class ChainClickManager(Manager):
    s_games = {}

    class ChainClickGame(object):
        def __init__(self, elements, chains):
            self.elements = elements
            self.chains = chains

    class Chain(object):
        def __init__(self, toWin):
            self.needToWin = toWin
            self.elements = []

        def appendElements(self, element):
            self.elements.append(element)

    @staticmethod
    def _onFinalize():
        ChainClickManager.s_games.clear()
        pass

    @staticmethod
    def loadGames(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            Name = record.get("Name")
            ElementsParam = record.get("Elements")
            ChainsParam = record.get("Chains")
            ElementToChainParam = record.get("ElementToChain")

            ChainClickManager.loadGame(Name, module, ElementsParam, ChainsParam, ElementToChainParam)

    @staticmethod
    def loadGame(name, module, elementsParam, chainsParam, elementToChainParam):
        elements = ChainClickManager.loadGameElements(module, elementsParam)
        gameChains = ChainClickManager.loadGameChains(module, chainsParam)
        ChainClickManager.loadGameElementToChain(module, elementToChainParam, elements)

        game = ChainClickManager.ChainClickGame(elements, gameChains)
        ChainClickManager.s_games[name] = game
        return game

    @staticmethod
    def loadGameElements(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        elements = {}
        for record in records:
            elementId = record.get("ElementId")
            objectName = record.get("ObjectName")
            clickedObjectName = record.get("ClickedObjectName")
            completeObjectName = record.get("CompleteObjectName")
            groupName = record.get("GroupName")

            elements[elementId] = dict(ObjectName=objectName, ClickedObjectName=clickedObjectName,
                                       CompleteObjectName=completeObjectName, GroupName=groupName)
        return elements

    @staticmethod
    def loadGameChains(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        chains = {}
        for record in records:
            ChainId = record.get("ChainId")
            NeedToWin = record.get("NeedToWin")
            chains[ChainId] = ChainClickManager.Chain(NeedToWin)
        return chains

    @staticmethod
    def loadGameElementToChain(module, param, chains):
        records = DatabaseManager.getDatabaseRecords(module, param)
        for record in records:
            ChainId = record.get("ChainId")
            ElementId = record.get("ElementId")
            if ChainId not in chains:
                Trace.log("Manager", 0, "ChainClickManager.loadGameElementToChain: invalid chain ID %i" % (ChainId))
            chain = chains[ChainId]
            chain.appendElements(ElementId)

    @staticmethod
    def getGame(name):
        if name not in ChainClickManager.s_games:
            Trace.log("Manager", 0, "ChainClickManager.getGame: not found game %s" % (name))
            return None
        game = ChainClickManager.s_games[name]
        return game

    @staticmethod
    def hasGame(name):
        return name in ChainClickManager.s_games
