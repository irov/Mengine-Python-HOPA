from Notification import Notification

class ConnectorsConnection(object):
    def __init__(self, socketObject, stateObject):
        self.elements = []
        self.socketObject = socketObject
        self.stateObject = stateObject
        self.stateObject.setCurrentState("onUp")
        self.active = False
        pass

    def initialize(self, callback):
        self.socketObject.setInteractive(True)
        self.onSocketClickObserver = Notification.addObserver(Notificator.onSocketClick, self._onSocketClick, self.socketObject, callback)
        self.onSocketMouseEnterObserver = Notification.addObserver(Notificator.onSocketMouseEnter, self._onSocketMouseEnter, self.socketObject)
        self.onSocketMouseLeaveObserver = Notification.addObserver(Notificator.onSocketMouseLeave, self._onSocketMouseLeave, self.socketObject)
        pass

    def finalize(self):
        Notification.removeObserver(self.onSocketClickObserver)
        Notification.removeObserver(self.onSocketMouseEnterObserver)
        Notification.removeObserver(self.onSocketMouseLeaveObserver)
        pass

    def addElement(self, element):
        self.elements.append(element)
        pass

    def increfElements(self):
        for element in self.elements:
            element.incref()
            pass
        pass

    def decrefElements(self):
        for element in self.elements:
            element.decref()
            pass
        pass

    def _onSocketClick(self, socket, wait, callback):
        if socket is not wait:
            return False
            pass

        if self.active == True:
            self.active = False
            self.decrefElements()
            self.stateObject.setCurrentState("onUp")
            pass
        else:
            self.active = True
            self.increfElements()
            self.stateObject.setCurrentState("onDown")
            pass

        callback()
        return False
        pass

    def _onSocketMouseEnter(self, socket, wait):
        if socket is not wait:
            return False
            pass

        currentState = self.stateObject.getCurrentState()
        if currentState == "onDown":
            return False
            pass

        self.stateObject.setCurrentState("onHover")
        return False
        pass

    def _onSocketMouseLeave(self, socket, wait):
        if socket is not wait:
            return False
            pass

        if self.active is True:
            return False
            pass

        self.stateObject.setCurrentState("onUp")
        return False
        pass
    pass