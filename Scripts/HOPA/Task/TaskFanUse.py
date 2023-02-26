from Foundation.ArrowManager import ArrowManager
from Foundation.Task.MixinObjectTemplate import MixinFan
from Foundation.Task.MixinObserver import MixinObserver
from Foundation.Task.Task import Task

class TaskFanUse(MixinFan, MixinObserver, Task):
    def _onParams(self, params):
        super(TaskFanUse, self)._onParams(params)

        self.Item = params.get("Item")
        pass

    def _onRun(self):
        self.addObserverFilter(Notificator.onFanClick, self._onFanClick, self.Fan)

        return False
        pass
    pass

    def _onFanClick(self, fan):
        if ArrowManager.emptyArrowAttach() is True:
            return False
            pass

        item = ArrowManager.getArrowAttach()

        if self.Item != item:
            return False
            pass

        return True
        pass