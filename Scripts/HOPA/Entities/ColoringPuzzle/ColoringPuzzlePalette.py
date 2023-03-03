from Notification import Notification


class ColoringPuzzlePalette(object):
    def __init__(self, color, socketObject):
        super(ColoringPuzzlePalette, self).__init__()
        self.socketObject = socketObject
        self.color = color
        self.onSocketClickObserver = None
        pass

    def initialize(self, callback):
        self.socketObject.setInteractive(True)
        self.onSocketClickObserver = Notification.addObserver(Notificator.onSocketClick, self._onSocketClick, self.socketObject, callback)
        pass

    def finalize(self):
        if self.onSocketClickObserver is not None:
            Notification.removeObserver(self.onSocketClickObserver)
            self.onSocketClickObserver = None
            pass
        pass

    def _onSocketClick(self, socket, wait, callback):
        if socket is not wait:
            return False
            pass

        callback(self.color)
        return False
