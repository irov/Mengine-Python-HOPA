from Foundation.Task.MixinObserver import MixinObserver
from Foundation.Task.Task import Task
from HOPA.ZoomManager import ZoomManager


class TaskZoomInterrupt(MixinObserver, Task):
    Skiped = True

    def _onRun(self):
        OpenZoom = ZoomManager.getZoomOpen()
        if OpenZoom is None:
            return True

        ZoomOpenGroupName = ZoomManager.getZoomOpenGroupName()

        ZoomManager.closeZoom(ZoomOpenGroupName)

        if OpenZoom.hasObject() is False:
            return True
            pass

        ZoomObject = OpenZoom.getObject()

        Enable = ZoomObject.getParam("Enable")

        if Enable is True:
            ZoomObject.setParam("Enable", False)
            pass

        return True
        pass

    pass
