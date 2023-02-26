from Foundation.Notificator import Notificator
from Foundation.TaskManager import TaskManager
from HOPA.CruiseAction import CruiseAction
from HOPA.CruiseControlManager import CruiseControlManager

class CruiseActionShiftCollect(CruiseAction):
    def _onCheck(self):
        return True

    def _onAction(self):
        click_delay = CruiseControlManager.getCruiseClickDelay('CruiseActionShiftCollect')
        if TaskManager.existTaskChain("CruiseActionShiftCollect") is True:
            TaskManager.cancelTaskChain("CruiseActionShiftCollect")

        with TaskManager.createTaskChain(Name="CruiseActionShiftCollect") as tc:
            tc.addDelay(click_delay)
            tc.addNotify(Notificator.onShiftCollectSkip)
            tc.addNotify(Notificator.onCruiseActionEnd, Args=(self,))