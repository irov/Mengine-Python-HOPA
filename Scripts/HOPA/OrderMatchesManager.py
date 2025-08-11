from Foundation.Manager import Manager

from Foundation.DatabaseManager import DatabaseManager

class OrderMatchesManager(object):
    s_games = {}

    class OrderMatchesGame(object):
        def __init__(self, elementsSource, elementsDestination, order):
            self.elementsSource = elementsSource
            self.elementsDestination = elementsDestination
            self.order = order

    @staticmethod
    def _onFinalize():
        OrderMatchesManager.s_games = {}
        pass

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            Name = record.get("Name")
            ElementsSourceParam = record.get("ElementsSource")
            ElementsDestinationParam = record.get("ElementsDestination")
            OrderParam = record.get("Order")

            OrderMatchesManager.loadGame(Name, module, ElementsSourceParam, ElementsDestinationParam, OrderParam)
            pass

        return True
        pass

    @staticmethod
    def loadGame(name, module, ElementsSourceParam, ElementsDestinationParam, OrderParam):
        if ElementsSourceParam is not None:
            elementsSource = OrderMatchesManager.loadGameElementsSource(module, ElementsSourceParam)
            pass
        else:
            elementsSource = None
            pass

        elementsDestination = OrderMatchesManager.loadGameElementsDestination(module, ElementsDestinationParam)
        order = OrderMatchesManager.loadGameOrder(module, OrderParam)

        game = OrderMatchesManager.OrderMatchesGame(elementsSource, elementsDestination, order)
        OrderMatchesManager.s_games[name] = game
        pass

    @staticmethod
    def loadGameElementsSource(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)
        elementsSource = {}
        for record in records:
            elementId = record.get("ElementId")
            objectName = record.get("ObjectName")
            elementsSource[elementId] = dict(ObjectName=objectName)
            pass
        return elementsSource
        pass

    @staticmethod
    def loadGameElementsDestination(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)
        elementsDestination = {}
        for record in records:
            elementId = record.get("ElementId")
            objectName = record.get("ObjectName")
            socketObjectName = record.get("SocketObjectName")
            MovieButton = record.get("MovieButton")
            elementsDestination[elementId] = dict(ObjectName=objectName,
                                                  SocketObjectName=socketObjectName,
                                                  MovieButton=MovieButton)

        return elementsDestination

    @staticmethod
    def loadGameOrder(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)
        orderList = []
        for record in records:
            order = record.get("Order")
            elementSourceId = record.get("ElementSourceId")
            elementDestinationId = record.get("ElementDestinationId")
            data = dict(Order=order, ElementDestinationId=elementDestinationId, ElementSourceId=elementSourceId)
            orderList.append(data)
            pass
        return orderList
        pass

    @staticmethod
    def getGame(name):
        if name not in OrderMatchesManager.s_games:
            Trace.log("Manager", 0, "OrderMatchesManager.getGame: not found game %s" % (name))
            return None
            pass
        game = OrderMatchesManager.s_games[name]
        return game
        pass

    @staticmethod
    def hasGame(name):
        return name in OrderMatchesManager.s_games
