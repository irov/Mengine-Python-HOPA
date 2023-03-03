from Foundation.Task.MixinObjectTemplate import MixinFan
from Foundation.Task.MixinObserver import MixinObserver
from Foundation.Task.Task import Task


class TaskFanClose(MixinFan, MixinObserver, Task):
    def _onRun(self):
        self.addObserverFilter(Notificator.onFanCloseDone, self.__onFanClose, self.Fan)

        return False
        pass

    def __onFanClose(self, fan):
        return True
        pass

    pass
