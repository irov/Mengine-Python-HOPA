from Foundation.ArrowManager import ArrowManager
from Foundation.Task.MixinObjectTemplate import MixinFan
from Foundation.Task.MixinObserver import MixinObserver
from Foundation.Task.Task import Task

class TaskFanClick(MixinFan, MixinObserver, Task):
    def _onParams(self, params):
        super(TaskFanClick, self)._onParams(params)

        self.AutoEnable = params.get("AutoEnable", True)
        pass

    def _onRun(self):
        if self.AutoEnable is True:
            self.Fan.setInteractive(True)
            pass

        self.addObserverFilter(Notificator.onFanClick, self._onFanClick, self.Fan)

        return False
        pass

    def _onFinally(self):
        super(TaskFanClick, self)._onFinally()

        if self.AutoEnable is True:
            self.Fan.setInteractive(False)
            pass
        pass

    def _onFanClick(self, fan):
        if ArrowManager.emptyArrowAttach() is False:
            return False
            pass

        return True
        pass
    pass