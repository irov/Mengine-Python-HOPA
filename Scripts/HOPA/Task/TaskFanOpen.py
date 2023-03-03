from Foundation.Task.MixinObjectTemplate import MixinFan
from Foundation.Task.MixinObserver import MixinObserver
from Foundation.Task.Task import Task


class TaskFanOpen(MixinFan, MixinObserver, Task):
    def _onRun(self):
        self.addObserverFilter(Notificator.onFanOpenDone, self.__onFanOpen, self.Fan)

        #        self.Fan.setOpen(True)
        return False
        pass

    def __onFanOpen(self, fan):
        return True
        pass

    pass
