from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.TaskManager import TaskManager


class OverclickHook(BaseEntity):
    def __init__(self):
        super(OverclickHook, self).__init__()

    def _onDeactivate(self):
        if TaskManager.existTaskChain("OverclickHook"):
            TaskManager.cancelTaskChain("OverclickHook")

    def _onActivate(self):
        with TaskManager.createTaskChain(Name="OverclickHook", Group=self.object, Repeat=True) as tc:
            tc.addTask("TaskSocketClick", SocketName="Socket_Overclick")
            tc.addNotify(Notificator.onOverclickHook)
