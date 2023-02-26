import Trace

from Foundation.DatabaseManager import DatabaseManager

class ChainClickManager(object):
    s_games = {}

    class ChainClickGame(object):
        def __init__(self, elements, chains):
            self.elements = elements
            self.chains = chains
            pass
        pass

    class Chain(object):
        def __init__(self, toWin):
            self.needToWin = toWin
            self.elements = []
            pass

        def appendElements(self, element):
            self.elements.append(element)
            pass
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
            pass
        pass

    @staticmethod
    def loadGame(name, module, elementsParam, chainsParam, elementToChainParam):
        elements = ChainClickManager.loadGameElements(module, elementsParam)
        gameChains = ChainClickManager.loadGameChains(module, chainsParam)
        ChainClickManager.loadGameElementToChain(module, elementToChainParam, elements)

        game = ChainClickManager.ChainClickGame(elements, gameChains)
        ChainClickManager.s_games[name] = game
        return game
        pass

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

            elements[elementId] = dict(ObjectName=objectName, ClickedObjectName=clickedObjectName, CompleteObjectName=completeObjectName, GroupName=groupName)
            pass
        return elements
        pass

    @staticmethod
    def loadGameChains(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        chains = {}
        for record in records:
            ChainId = record.get("ChainId")
            NeedToWin = record.get("NeedToWin")
            chains[ChainId] = ChainClickManager.Chain(NeedToWin)
            pass
        return chains
        pass

    @staticmethod
    def loadGameElementToChain(module, param, chains):
        records = DatabaseManager.getDatabaseRecords(module, param)
        for record in records:
            ChainId = record.get("ChainId")
            ElementId = record.get("ElementId")
            if ChainId not in chains:
                Trace.log("Manager", 0, "ChainClickManager.loadGameElementToChain: invalid chain ID %i" % (ChainId))
                pass
            chain = chains[ChainId]
            chain.appendElements(ElementId)
            pass
        pass

    @staticmethod
    def getGame(name):
        if name not in ChainClickManager.s_games:
            Trace.log("Manager", 0, "ChainClickManager.getGame: not found game %s" % (name))
            return None
            pass
        game = ChainClickManager.s_games[name]
        return game
        pass

    @staticmethod
    def hasGame(name):
        return name in ChainClickManager.s_games
        pass

    pass