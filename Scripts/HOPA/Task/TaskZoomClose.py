from HOPA.Task.MixinZoomGroup import MixinZoomGroup
from HOPA.ZoomManager import ZoomManager

from Foundation.Task.MixinObserver import MixinObserver
from Foundation.Task.Task import Task

class TaskZoomClose(MixinZoomGroup, MixinObserver, Task):
    Skiped = True

    def _onParams(self, params):
        super(TaskZoomClose, self)._onParams(params)

        self.value = params.get("Value", True)
        pass

    def _onCheck(self):
        Zoom = ZoomManager.getZoom(self.ZoomGroupName)
        Open = Zoom.getOpen()
        if Open is not self.value:
            return False
            pass

        return True
        pass

    def _onRun(self):
        if self.value is False:
            ZoomManager.openZoom(self.ZoomGroupName)
            self.addObserverFilter(Notificator.onZoomEnter, self._onZoomEnterFilter, self.ZoomGroupName)
            return False
            pass
        else:
            ZoomManager.closeZoom(self.ZoomGroupName)
            self.addObserverFilter(Notificator.onZoomLeave, self._onZoomEnterFilter, self.ZoomGroupName)
            return False
            pass

        return False
        pass
    pass

    def _onZoomEnterFilter(self, zoomGroupName):
        return True
        pass