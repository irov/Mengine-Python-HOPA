from Foundation.Task.MixinObject import MixinObject
from Foundation.Task.MixinObserver import MixinObserver
from Foundation.Task.Task import Task


class TaskAnimatableButtonLeave(MixinObject, MixinObserver, Task):
    def _onParams(self, params):
        super(TaskAnimatableButtonLeave, self)._onParams(params)
        pass

    def _onCheck(self):
        if self.Object.isActive() is True:
            ButtonEntity = self.Object.getEntity()
            if ButtonEntity.isMouseEnter() is False:
                return False
                pass
            pass

        return True
        pass

    def _onRun(self):
        self.addObserverFilter(Notificator.onAnimatableButtonMouseLeave, self._onButtonMouseLeaveFilter, self.Object)

        return False
        pass

    def _onButtonMouseLeaveFilter(self, Button):
        return True
        pass

    pass
