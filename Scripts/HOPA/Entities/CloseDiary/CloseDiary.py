from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.TaskManager import TaskManager

class CloseDiary(BaseEntity):

    def _onActivate(self):
        super(CloseDiary, self)._onActivate()
        self.cancelTaskChains()
        if self.object.hasObject("Button_Close") is True:
            Button = self.object.getObject("Button_Close")
        with TaskManager.createTaskChain(Name="CloseDiary") as tc:
            tc.addTask("TaskButtonClick", Button=Button)
            tc.addTask("TaskNotify", ID=Notificator.onDiaryClose)
            pass
        pass

    def _onDeactivate(self):
        super(CloseDiary, self)._onDeactivate()
        self.cancelTaskChains()
        pass

    def cancelTaskChains(self):
        if TaskManager.existTaskChain("CloseDiary") is True:
            TaskManager.cancelTaskChain("CloseDiary")
            pass
    pass