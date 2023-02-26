from Foundation.Task.MixinObserver import MixinObserver
from Foundation.Task.Task import Task

class TaskDialogSkip(MixinObserver, Task):
    Skiped = False

    def _onParams(self, params):
        super(TaskDialogSkip, self)._onParams(params)

        self.DialogID = params.get("DialogID")
        pass

    def _onRun(self):
        def __onDialogCloseFilter(dialogID, dialog):
            return True
            pass

        self.addObserverFilter(Notificator.onDialogSkip, __onDialogCloseFilter, self.DialogID)

        return False
        pass
    pass