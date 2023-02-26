from Foundation.Task.MixinObject import MixinObject
from Foundation.Task.MixinObserver import MixinObserver
from Foundation.Task.Task import Task

class TaskAnimatableButtonEnter(MixinObject, MixinObserver, Task):
    def _onParams(self, params):
        super(TaskAnimatableButtonEnter, self)._onParams(params)
        pass

    def _onCheck(self):
        if self.Object.isActive() is True:
            ButtonEntity = self.Object.getEntity()
            if ButtonEntity.isMouseEnter() is True:
                return False
                pass
            pass

        return True
        pass

    def _onRun(self):
        self.addObserverFilter(Notificator.onAnimatableButtonMouseEnter, self._onButtonMouseEnterFilter, self.Object)

        return False
        pass

    def _onButtonMouseEnterFilter(self, Button):
        return True
        pass
    pass