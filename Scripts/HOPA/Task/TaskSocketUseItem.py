from Foundation.ArrowManager import ArrowManager
from Foundation.Task.MixinObjectTemplate import MixinItem
from Foundation.Task.MixinObserver import MixinObserver
from Foundation.Task.Task import Task

class TaskSocketUseItem(MixinItem, MixinObserver, Task):
    Skiped = False

    def _onParams(self, params):
        super(TaskSocketUseItem, self)._onParams(params)
        self.AutoEnable = params.get("AutoEnable", True)
        self.Socket = params.get("Socket")
        self.taken = params.get("Taken", True)

    def _onRun(self):
        if self.AutoEnable is True:
            self.Socket.setInteractive(True)

        # remove onSocketClickEndUp for Touchpad because it causes bugs in click+click
        self.addObserverFilter(Notificator.onSocketClick, self._onPlaceSocketFilter, self.Socket)

        return False

    def _onFinally(self):
        super(TaskSocketUseItem, self)._onFinally()

        if self.AutoEnable is True:
            self.Socket.setInteractive(False)

    def _onPlaceSocketFilter(self, socket):
        attach = ArrowManager.getArrowAttach()

        if attach is not None and attach is not self.Item:
            Notification.notify(Notificator.onSocketUseItemInvalidUse, None, self.Socket)
            return False

        if attach is None or attach is not self.Item:
            return False

        if self.taken is True:
            ArrowManager.removeArrowAttach()

        return True