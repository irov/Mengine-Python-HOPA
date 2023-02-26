from Foundation.ArrowManager import ArrowManager
from Foundation.Task.MixinObserver import MixinObserver
from Foundation.Task.Task import Task
from Foundation.Task.c import MixinObject

class TaskAnimatableButtonClick(MixinObject, MixinObserver, Task):
    def _onParams(self, params):
        super(TaskAnimatableButtonClick, self)._onParams(params)

        self.AutoEnable = params.get("AutoEnable", True)
        pass

    def _onRun(self):
        if self.AutoEnable is True:
            self.Object.setInteractive(True)
            pass

        self.addObserverFilter(Notificator.onAnimatableButtonClick, self._onButtonClick, self.Object)

        return False
        pass

    def _onFinally(self):
        super(TaskAnimatableButtonClick, self)._onFinally()

        if self.AutoEnable is True:
            self.Object.setInteractive(False)
            pass
        pass

    def _onButtonClick(self, button):
        if ArrowManager.emptyArrowAttach() is False:
            return False
            pass

        return True
        pass

    pass