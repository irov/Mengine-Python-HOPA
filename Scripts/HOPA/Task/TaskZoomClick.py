from Foundation.Task.MixinObjectTemplate import MixinZoom
from Foundation.Task.MixinObserver import MixinObserver
from Foundation.Task.Task import Task


class TaskZoomClick(MixinZoom, MixinObserver, Task):
    def _onParams(self, params):
        super(TaskZoomClick, self)._onParams(params)

        self.AutoEnable = params.get("AutoEnable", True)
        pass

    def _onRun(self):
        if self.AutoEnable is True:
            self.Zoom.setInteractive(True)
            pass

        self.addObserverFilter(Notificator.onZoomClick, self._onZoomClickFilter, self.Zoom)

        return False
        pass

    def _onFinally(self):
        super(TaskZoomClick, self)._onFinally()

        if self.AutoEnable is True:
            self.Zoom.setInteractive(False)
            pass
        pass

    def _onZoomClickFilter(self, zoom):
        return True
        pass

    pass
