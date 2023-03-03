from Foundation.Task.MixinObserver import MixinObserver
from Foundation.Task.Task import Task


class TaskFanItemInvalidUse(MixinObserver, Task):
    def _onParams(self, params):
        super(TaskFanItemInvalidUse, self)._onParams(params)

        self.FanItem = params.get("FanItem")
        pass

    def _onRun(self):
        self.addObserverFilter(Notificator.onFanItemInvalidUse, self._onFanItemInvalidUse, self.FanItem)

        return False
        pass

    def _onFanItemInvalidUse(self, item):
        return True
        pass

    pass
