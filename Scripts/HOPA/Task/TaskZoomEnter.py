from HOPA.Task.MixinZoomGroup import MixinZoomGroup

from Foundation.Task.MixinObserver import MixinObserver
from Foundation.Task.Task import Task

class TaskZoomEnter(MixinZoomGroup, MixinObserver, Task):
    Skiped = False

    def _onParams(self, params):
        super(TaskZoomEnter, self)._onParams(params)
        self.isEnter = params.get("isEnter", True)
        pass

    def _onRun(self):
        if self.isEnter is True:
            if self.isZoomEnter() is True:
                return True
                pass
            pass

        self.addObserver(Notificator.onZoomEnter, self._onZoomFilter)

        return False
        pass
    pass