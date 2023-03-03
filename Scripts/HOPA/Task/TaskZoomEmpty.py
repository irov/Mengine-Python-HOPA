from Foundation.Task.MixinObserver import MixinObserver
from Foundation.Task.Task import Task
from HOPA.ZoomManager import ZoomManager


class TaskZoomEmpty(MixinObserver, Task):
    Skiped = False

    def _onCheck(self):
        if ZoomManager.isZoomEmpty() is True:
            return False
            pass

        return True
        pass

    def _onRun(self):
        self.addObserver(Notificator.onZoomEmpty, self._onZoomEmptyFilter)

        return False
        pass

    def _onZoomEmptyFilter(self):
        return True
        pass

    pass
