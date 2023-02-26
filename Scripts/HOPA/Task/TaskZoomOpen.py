from HOPA.Task.MixinZoomGroup import MixinZoomGroup
from HOPA.ZoomManager import ZoomManager

from Foundation.Task.MixinObserver import MixinObserver
from Foundation.Task.Task import Task


class TaskZoomOpen(MixinZoomGroup, MixinObserver, Task):
    Skiped = True

    def _onParams(self, params):
        super(TaskZoomOpen, self)._onParams(params)

        self.value = params.get("Value", True)
        pass

    def _onCheck(self):
        Zoom = ZoomManager.getZoom(self.ZoomGroupName)
        Open = Zoom.getOpen()
        if Open is self.value:
            return False
            pass

        return True
        pass

    def _onRun(self):
        if self.value is False:
            ZoomManager.closeZoom(self.ZoomGroupName)
            return True
            pass

        ZoomManager.openZoom(self.ZoomGroupName)

        self.addObserverFilter(Notificator.onZoomEnter, self._onZoomEnterFilter, self.ZoomGroupName)

        return False
        pass
    pass

    def _onZoomEnterFilter(self, zoomGroupName):
        return True
        pass
    pass