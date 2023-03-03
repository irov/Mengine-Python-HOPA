from Foundation.ArrowManager import ArrowManager
from Foundation.Task.MixinObject import MixinObject
from Foundation.Task.MixinObserver import MixinObserver
from Foundation.Task.Task import Task


class TaskAnimatableButtonClickEndUp(MixinObject, MixinObserver, Task):
    def _onParams(self, params):
        super(TaskAnimatableButtonClickEndUp, self)._onParams(params)

        self.AutoEnable = params.get("AutoEnable", True)
        pass

    def _onRun(self):
        if self.AutoEnable is True:
            self.Object.setInteractive(True)
            pass

        self.addObserverFilter(Notificator.onButtonClickEndUp, self._onButtonClick, self.Object)

        return False
        pass

    def _onFinally(self):
        super(TaskAnimatableButtonClickEndUp, self)._onFinally()

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
