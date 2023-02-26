from Foundation.ArrowManager import ArrowManager
from Foundation.Task.MixinObserver import MixinObserver
from Foundation.Task.Task import Task

class TaskHintClick(MixinObserver, Task):
    def _onParams(self, params):
        super(TaskHintClick, self)._onParams(params)

        self.Hint = params.get("Hint")
        pass

    def _onRun(self):
        self.addObserverFilter(Notificator.onHintClick, self._onHintClick, self.Hint)

        return False
        pass

    def _onHintClick(self, Hint, valid):
        if ArrowManager.emptyArrowAttach() is False:
            return False
            pass

        return True
        pass
    pass