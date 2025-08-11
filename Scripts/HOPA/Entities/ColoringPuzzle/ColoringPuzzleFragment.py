class ColoringPuzzleFragment(object):
    def __init__(self, stateObject, socketObject):
        super(ColoringPuzzleFragment, self).__init__()
        self.socketObject = socketObject
        self.stateObject = stateObject
        self.color = None
        self.onSocketClickObserver = None
        pass

    def initialize(self, callback):
        self.socketObject.setInteractive(True)
        self.onSocketClickObserver = Notification.addObserver(Notificator.onSocketClickEndUp, self._onSocketClick, self.socketObject, callback)
        pass

    def finalize(self):
        if self.onSocketClickObserver is not None:
            Notification.removeObserver(self.onSocketClickObserver)
            self.onSocketClickObserver = None
            pass
        pass

    def getColor(self):
        return self.color
        pass

    def setColor(self, color):
        if self.color is color:
            return
            pass

        self.color = color
        self.updateView()
        pass

    def updateView(self):
        colorName = self.color.getColorName()

        if self.stateObject.hasState(colorName) is False:
            Trace.log("Manager", 0, "setColor color  not  supported %s" % colorName)
            return False
            pass

        self.stateObject.setCurrentState(colorName)
        pass

    def _onSocketClick(self, socket, wait, callback):
        if socket is not wait:
            return False
            pass

        callback(self)
        return False