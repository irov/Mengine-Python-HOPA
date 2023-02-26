from Foundation.TaskManager import TaskManager
from HOPA.OrderMatchesManager import OrderMatchesManager
from Notification import Notification

class OrderMatchesElementSource(object):
    def __init__(self, stateObjectObject):
        super(OrderMatchesElementSource, self).__init__()
        self.stateObject = stateObjectObject
        self.stateObject.setCurrentState("Wait")
        pass

    def setComplete(self):
        self.stateObject.setCurrentState("Complete")
        pass

    def setActive(self):
        self.stateObject.setCurrentState("Active")
        pass

    def setWait(self):
        self.stateObject.setCurrentState("Wait")
        pass
    pass

class OrderMatchesElementDestination(object):
    def __init__(self, elementType, stateObjectObject, socketObject, movButtonName, MovieButtonGroup):
        super(OrderMatchesElementDestination, self).__init__()
        self.elementType = elementType
        self.stateObject = stateObjectObject
        self.stateObject.setCurrentState("Wait")
        self.socketObject = socketObject
        self.MovieButtonName = movButtonName
        self.MovieButtonGroup = MovieButtonGroup
        self.complete = False

        self.onSocketClickObserver = None
        pass

    def initialize(self, callback):
        self.socketObject.setInteractive(True)
        self.onSocketClickObserver = Notification.addObserver(Notificator.onSocketClick, self._onSocketClick, self.socketObject, callback)
        # MAYBE NEED FOR FUTURE
        # self.onSocketMouseEnterObserver = Notification.addObserver("onSocketMouseEnter", Functor(self._onSocketMouseEnter, self.socketObject))
        # self.onSocketMouseLeaveObserver = Notification.addObserver("onSocketMouseLeave", Functor(self._onSocketMouseLeave, self.socketObject))
        def fun():
            if self.complete is True:
                return False
                pass

            callback(self.elementType)
            pass

        if self.MovieButtonName is not None:
            but = self.MovieButtonGroup.getObject(self.MovieButtonName)
            nameChain = "Order %s" % (self.MovieButtonName)
            with TaskManager.createTaskChain(Name=nameChain, Repeat=True) as tc:
                # with TaskManager.createTaskChain(Name = nameChain, GroupName = self.MovieButtonGroup, Repeat = True) as tc:
                # tc.addTask("TaskButtonClick", ButtonName = self.MovieButtonName)
                tc.addTask("TaskButtonClick", Button=but)
                tc.addTask("TaskFunction", Fn=fun)
                pass
            pass

        pass

    def setComplete(self):
        self.complete = True
        self.stateObject.setCurrentState("Complete")
        pass

    def setWait(self):
        self.complete = False
        self.stateObject.setCurrentState("Wait")
        pass

    def finalize(self):
        Notification.removeObserver(self.onSocketClickObserver)

        if self.MovieButtonName is not None:
            nameChain = "Order %s" % (self.MovieButtonName)
            if TaskManager.existTaskChain(nameChain) is True:
                TaskManager.cancelTaskChain(nameChain)
                pass
            pass
        # MAYBE NEED FOR FUTURE
        # Notification.removeObserver(self.onSocketMouseEnterObserver)
        # Notification.removeObserver(self.onSocketMouseLeaveObserver)
        pass

    def _onSocketClick(self, socket, wait, callback):
        if socket is not wait:
            return False
            pass

        if self.complete is True:
            return False
            pass

        callback(self.elementType)
        return False
        pass

    #    def _onSocketMouseEnter(self, socket, wait):
    #        #MAYBE NEED FOR FUTURE
    #        return False
    #        pass
    #
    #    def _onSocketMouseLeave(self, socket, wait):
    #        #MAYBE NEED FOR FUTURE
    #        return False
    #        pass
    pass

Enigma = Mengine.importEntity("Enigma")

class OrderMatches(Enigma):
    def __init__(self):
        super(OrderMatches, self).__init__()
        self.elementsDestination = {}
        self.elementsSource = {}
        self.order = []
        self.currentOrderIndex = -1
        pass

    def finalize(self):
        for elementId, element in self.elementsDestination.items():
            element.finalize()
            pass

        self.elementsDestination = {}
        self.elementsSource = {}
        self.order = []
        self.currentOrderIndex = -1
        pass

    def _autoWin(self):
        self.finalize()
        self.enigmaComplete()
        pass

    def _stopEnigma(self):
        self.finalize()
        pass

    def _skipEnigma(self):
        self._autoWin()
        pass

    def isRightTurn(self, elementId):
        currentOrder = self.order[self.currentOrderIndex]

        if currentOrder["ElementDestinationId"] != elementId:
            return False
            pass

        return True
        pass

    def _restoreEnigma(self):
        self._playEnigma()
        pass

    def reset(self):
        for turnId in range(self.currentOrderIndex + 1):
            turn = self.order[turnId]

            if len(self.elementsSource) != 0:
                sourceId = turn["ElementSourceId"]
                elementSource = self.elementsSource[sourceId]
                elementSource.setWait()
                pass

            destinationId = turn["ElementDestinationId"]
            elementDestination = self.elementsDestination[destinationId]
            elementDestination.setWait()
            pass
        self.currentOrderIndex = -1
        pass

    def completeTurn(self):
        currentOrder = self.order[self.currentOrderIndex]

        if len(self.elementsSource) != 0:
            sourceId = currentOrder["ElementSourceId"]
            elementSource = self.elementsSource[sourceId]
            elementSource.setComplete()
            pass

        destinationId = currentOrder["ElementDestinationId"]
        elementDestination = self.elementsDestination[destinationId]
        elementDestination.setComplete()

        if TaskManager.existTaskChain("Play_Complete") is True:
            return
            pass

        if self.object.hasObject("Movie_Sound_RightClick") is True:
            with TaskManager.createTaskChain(Name="Play_Complete", Group=self.object) as tc:
                tc.addTask("TaskMoviePlay", MovieName="Movie_Sound_RightClick")
                pass
            pass
        pass

    def allowNextTurn(self):
        self.currentOrderIndex += 1
        currentOrder = self.order[self.currentOrderIndex]

        if len(self.elementsSource) != 0:
            sourceId = currentOrder["ElementSourceId"]
            elementSource = self.elementsSource[sourceId]
            elementSource.setActive()
            pass
        pass

    def isComplete(self):
        if self.currentOrderIndex == (len(self.order) - 1):
            return True
            pass
        return False
        pass

    def _checkComplete(self, elementType):
        if self.isRightTurn(elementType) is False:
            self.reset()
            self.allowNextTurn()
            return False
            pass

        self.completeTurn()
        if self.isComplete() is False:
            self.allowNextTurn()
            return False
            pass

        self.finalize()
        self.enigmaComplete()
        return True
        pass

    def _onActivate(self):
        super(OrderMatches, self)._onActivate()

        GameData = OrderMatchesManager.getGame(self.EnigmaName)
        self.order = sorted(GameData.order, key=lambda x: x["Order"])

        if GameData.elementsSource is not None:
            for elementId, elementData in GameData.elementsSource.items():
                stateObject = self.object.getObject(elementData["ObjectName"])
                element = OrderMatchesElementSource(stateObject)
                self.elementsSource[elementId] = element
                pass
            pass

        for elementId, elementData in GameData.elementsDestination.items():
            stateObject = self.object.getObject(elementData["ObjectName"])
            socketObject = self.object.getObject(elementData["SocketObjectName"])
            MovieButtonName = elementData["MovieButton"]
            # MovieButtonGroup = self.object.getParent().name
            # MovieButtonGroup = self.object.getParent()
            MovieButtonGroup = self.object
            element = OrderMatchesElementDestination(elementId, stateObject, socketObject, MovieButtonName, MovieButtonGroup)
            self.elementsDestination[elementId] = element
            pass
        pass

    def _onDeactivate(self):
        super(OrderMatches, self)._onDeactivate()
        self.finalize()
        pass

    def _playEnigma(self):
        for elementId, element in self.elementsDestination.items():
            element.initialize(self._checkComplete)
            pass

        self.allowNextTurn()
        pass

    def _resetEnigma(self):
        self.reset()
        pass

    pass