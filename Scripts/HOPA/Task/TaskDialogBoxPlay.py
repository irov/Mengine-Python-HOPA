from Foundation.Task.MixinObserver import MixinObserver
from Foundation.Task.Task import Task
from HOPA.DialogBoxManager import DialogBoxManager


class TaskDialogBoxPlay(MixinObserver, Task):
    Skiped = True

    def _onParams(self, params):
        super(TaskDialogBoxPlay, self)._onParams(params)
        self.DialogID = params.get("DialogID")
        pass

    def _onInitialize(self):
        super(TaskDialogBoxPlay, self)._onInitialize()

        if _DEVELOPMENT is True:
            if DialogBoxManager.hasDialog(self.DialogID) is False:
                self.initializeFailed("DialogID %s not found" % (self.DialogID))
                pass
            pass
        pass

    def _onRun(self):
        self.addObserverFilter(Notificator.onDialogBoxPlayComplete, self._onDialogBoxShowComplete, self.DialogID)

        Notification.notify(Notificator.onDialogBoxShowRelease, self.DialogID)
        Notification.notify(Notificator.onDialogBoxShow, self.DialogID)

        return True
        pass

    def _onDialogBoxShowComplete(self, dialogID):
        if self.DialogID != dialogID:
            return False
            pass

        return True
        pass
