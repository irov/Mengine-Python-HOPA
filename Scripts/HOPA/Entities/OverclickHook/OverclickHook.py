from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.TaskManager import TaskManager

class OverclickHook(BaseEntity):
    def __init__(self):
        super(OverclickHook, self).__init__()

        pass

    def _onDeactivate(self):
        if TaskManager.existTaskChain("OverclickHook"):
            TaskManager.cancelTaskChain("OverclickHook")
            pass

        pass

    def _onActivate(self):
        with TaskManager.createTaskChain(Name="OverclickHook", Group=self.object, Repeat=True) as tc:
            tc.addTask("TaskSocketClick", SocketName="Socket_Overclick")
            tc.addTask("TaskNotify", ID=Notificator.onOverclickHook)
            pass
        pass

    pass