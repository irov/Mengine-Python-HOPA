from Foundation.Notificator import Notificator
from Foundation.TaskManager import TaskManager
from HOPA.CruiseAction import CruiseAction

class CruiseActionDummy(CruiseAction):
    def _onAction(self):
        if TaskManager.existTaskChain("CruiseActionDummy") is True:
            TaskManager.cancelTaskChain("CruiseActionDummy")

        with TaskManager.createTaskChain(Name="CruiseActionDummy") as tc:
            tc.addTask("TaskListener", ID=Notificator.onQuestEnd, Filter=lambda quest: quest == self.Quest)
            tc.addTask("TaskNotify", ID=Notificator.onCruiseActionEnd, Args=(self,))