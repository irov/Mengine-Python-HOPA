from Foundation.Task.MixinObserver import MixinObserver
from Foundation.Task.Task import Task

class TaskItemInvalidUse(MixinObserver, Task):
    def _onParams(self, params):
        super(TaskItemInvalidUse, self)._onParams(params)

        self.Item = params.get("Item")
        pass

    def _onRun(self):
        self.addObserverFilter(Notificator.onItemInvalidUse, self._onItemInvalidUse, self.Item)

        return False
        pass

    def _onItemInvalidUse(self, item):
        return True
        pass
    pass