from Foundation.Notificator import Notificator
from Foundation.SystemManager import SystemManager
from Foundation.TaskManager import TaskManager
from HOPA.CruiseAction import CruiseAction
from HOPA.CruiseControlManager import CruiseControlManager
from HOPA.HintManager import HintManager


class CruiseActionHint(CruiseAction):
    def __init__(self):
        super(CruiseActionHint, self).__init__()
        self.Point = None
        self.click_delay = CruiseControlManager.getCruiseClickDelay('CruiseActionHint')
        self.move_delay = CruiseControlManager.getCruiseMoveDelay('CruiseActionHint')

    def _onCheck(self):
        SystemHint = SystemManager.getSystem("SystemHint")
        DemonHint = SystemHint.getHintObject()

        if not DemonHint.isActive():
            return False

        Entity = DemonHint.getEntity()

        if Entity is None:
            return False

        hintAction = Entity.hintGive()

        if hintAction is None:
            hintAction = HintManager.findGlobalHint(DemonHint)

            if hintAction is None:
                return False

        hintActionObj = hintAction.getHintObject()
        if hintActionObj is None:
            return False

        self.Point = hintAction.getHintPosition(hintActionObj)

        if self.Point is None:
            return False

        return True

    def _onAction(self):
        Obj = self.Quest.params.get("Object", None) if self.Quest else None

        if TaskManager.existTaskChain("CruiseActionDefault") is True:
            TaskManager.cancelTaskChain("CruiseActionDefault")

        with TaskManager.createTaskChain(Name="CruiseActionDefault") as tc:
            tc.addDelay(self.click_delay)
            tc.addTask("AliasCruiseControlAction", Position=self.Point, Object=Obj)
            tc.addDelay(self.move_delay)
            tc.addNotify(Notificator.onCruiseActionEnd, self)

    def _onEnd(self):
        if TaskManager.existTaskChain("CruiseActionDefault") is True:
            TaskManager.cancelTaskChain("CruiseActionDefault")
