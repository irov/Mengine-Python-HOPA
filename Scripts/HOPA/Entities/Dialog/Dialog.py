from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.PolicyManager import PolicyManager
from Foundation.TaskManager import TaskManager
from Functor import Functor

class Dialog(BaseEntity):
    def __init__(self):
        super(Dialog, self).__init__()

        self.curID = None
        pass

    def showBlackBar(self, dialogID):
        self._openDialog(dialogID)
        return False
        pass

    def releaseBlackBar(self, currentID=None):
        if TaskManager.existTaskChain("DialogMessage"):
            TaskManager.skipTaskChain("DialogMessage")
            pass

        if TaskManager.existTaskChain("DialogMessage"):
            TaskManager.cancelTaskChain("DialogMessage")

            Notification.notify(Notificator.onDialogSkip, self.curID, self.object)
            pass

        return False
        pass

    def _openDialog(self, dialogID):
        self.curID = dialogID

        if _DEVELOPMENT is True:
            Trace.msg("<Dialog> open '%s'" % self.curID)

        with TaskManager.createTaskChain(Name="DialogMessage", Group=self.object, Cb=Functor(self._dialogEnd, dialogID)) as tc:
            DialogPolicy = PolicyManager.getPolicy("Dialog", "PolicyMonologue")
            tc.addTask(DialogPolicy, DialogID=dialogID, Dialog=self.object)

    def _dialogEnd(self, isEnd, dialogID):
        Notification.notify(Notificator.onDialogHide, dialogID, self.object)
        pass

    def _onActivate(self):
        super(Dialog, self)._onActivate()

        self.onDialogShow = Notification.addObserver(Notificator.onDialogShow, self.showBlackBar)
        self.onBlackBarRelease = Notification.addObserver(Notificator.onBlackBarRelease, self.releaseBlackBar)
        pass

    def _onDeactivate(self):
        super(Dialog, self)._onDeactivate()

        Notification.removeObserver(self.onDialogShow)
        Notification.removeObserver(self.onBlackBarRelease)

        if TaskManager.existTaskChain("DialogMessage"):
            TaskManager.cancelTaskChain("DialogMessage")

            Notification.notify(Notificator.onDialogSkip, self.curID, self.object)
