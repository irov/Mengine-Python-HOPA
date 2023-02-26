from Foundation.Notificator import Notificator
from Foundation.Task.MixinObjectTemplate import MixinTransition
from Foundation.TaskManager import TaskManager
from HOPA.CruiseAction import CruiseAction
from HOPA.CruiseControlManager import CruiseControlManager

class CruiseActionTransition(MixinTransition, CruiseAction):

    def _onCheck(self):
        return self.Transition.isActive()

    def _getCruiseObject(self):
        return self.Transition

    def _onAction(self):
        self.move_delay = CruiseControlManager.getCruiseMoveDelay('CruiseActionTransition')

        if TaskManager.existTaskChain("CruiseActionTransition") is True:
            TaskManager.cancelTaskChain("CruiseActionTransition")

        with TaskManager.createTaskChain(Name="CruiseActionTransition") as tc:
            tc.addDelay(self.move_delay)
            tc.addTask("AliasCruiseControlAction", Position=self.Transition.calcWorldHintPoint(), Object=self._getCruiseObject())
            tc.addTask("TaskNotify", ID=Notificator.onCruiseActionEnd, Args=(self,))

    def _onEnd(self):
        if TaskManager.existTaskChain("CruiseActionTransition") is True:
            TaskManager.cancelTaskChain("CruiseActionTransition")