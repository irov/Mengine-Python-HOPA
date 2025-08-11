from Foundation.Manager import Manager

from Foundation.DatabaseManager import DatabaseManager

class SwapDifferentManager(Manager):
    s_games = {}

    class SwapDifferentGame(object):
        def __init__(self, elements, rules):
            self.elements = elements
            self.rules = rules

    @staticmethod
    def _onFinalize():
        SwapDifferentManager.s_games = {}
        pass

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            Name = record.get("Name")
            ElementsParam = record.get("Elements")
            RulesParam = record.get("Rules")

            SwapDifferentManager.loadGame(Name, ElementsParam, RulesParam)

    @staticmethod
    def loadGame(name, elementsParam, RulesParam):
        elements = SwapDifferentManager.loadGameElements(elementsParam)
        rules = SwapDifferentManager.loadGameRules(RulesParam)

        game = SwapDifferentManager.SwapDifferentGame(elements, rules)
        SwapDifferentManager.s_games[name] = game
        return game
        pass

    @staticmethod
    def loadGameElements(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        elements = {}
        for record in records:
            ElementId = record.get("ElementId")
            ObjectName = record.get("ObjectName")
            StartOrder = record.get("StartOrder")
            elements[ElementId] = dict(ObjectName=ObjectName, StartOrder=StartOrder)
            pass
        return elements
        pass

    @staticmethod
    def loadGameRules(param):
        records = DatabaseManager.getDatabaseRecords(param)

        rules = {}
        for record in records:
            Order = record.get("Order")
            ElementId = record.get("ElementId")
            rules[ElementId] = Order
            pass
        return rules
        pass

    @staticmethod
    def getGame(name):
        if name not in SwapDifferentManager.s_games:
            Trace.log("Manager", 0, "SwapDifferentManager.getGame: not found game %s" % (name))
            return None
            pass
        game = SwapDifferentManager.s_games[name]
        return game
        pass

    @staticmethod
    def hasGame(name):
        return name in SwapDifferentManager.s_games
