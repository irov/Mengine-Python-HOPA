from Foundation.Task.MixinObserver import MixinObserver
from Foundation.Task.Task import Task
from HOPA.FanManager import FanManager


class TaskFanComplete(MixinObserver, Task):
    def _onParams(self, params):
        super(TaskFanComplete, self)._onParams(params)

        self.FanName = params.get("FanName")
        self.Fan = None
        pass

    def _onInitialize(self):
        super(TaskFanComplete, self)._onInitialize()

        if _DEVELOPMENT is True:
            if FanManager.hasFan(self.FanName) is False:
                self.initializeFailed("TaskFanComplete: invalid FanName '%s'" % (self.FanName))
                pass
            pass

        self.Fan = FanManager.getFanObject(self.FanName)
        pass

    def _onRun(self):
        self.addObserverFilter(Notificator.onFanComplete, self._onFanComplete, self.Fan)

        return False
        pass

    def _onFanComplete(self, fan):
        return True
        pass

    pass
