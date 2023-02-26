from Foundation.Notificator import Notificator
from Foundation.Task.MixinGroup import MixinGroup
from Foundation.TaskManager import TaskManager
from HOPA.CruiseAction import CruiseAction

class CruiseActionWait(MixinGroup, CruiseAction):
    def _onAction(self):
        if TaskManager.existTaskChain("CruiseActionWait") is True:
            TaskManager.cancelTaskChain("CruiseActionWait")

        with TaskManager.createTaskChain(Name="CruiseActionWait") as tc:
            tc.addTask("TaskListener", ID=Notificator.onQuestRun)
            tc.addTask("TaskNotify", ID=Notificator.onCruiseActionEnd, Args=(self,))