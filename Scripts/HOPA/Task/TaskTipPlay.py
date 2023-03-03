from Foundation.Task.MixinObject import MixinObject
from Foundation.Task.Task import Task
from Notification import Notification


class TaskTipPlay(MixinObject, Task):
    Skiped = True

    def _onParams(self, params):
        super(TaskTipPlay, self)._onParams(params)

        self.tipID = params.get("TipID")
        self.notifies = params.get("Notifies", [])
        pass

    def _onRun(self):
        Notification.notify(Notificator.onTipActivate, self.Object, self.tipID, self.notifies)

        return True
        pass

    pass
