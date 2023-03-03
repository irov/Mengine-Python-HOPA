from Foundation.GroupManager import GroupManager
from Foundation.Task.MixinObjectTemplate import MixinTransition
from Foundation.TaskManager import TaskManager
from HOPA.CruiseActions.CruiseActionDefault import CruiseActionDefault
from HOPA.CruiseControlManager import CruiseControlManager


class CruiseActionTransitionBack(MixinTransition, CruiseActionDefault):

    def _onParams(self, params):
        super(CruiseActionTransitionBack, self)._onParams(params)
        self.click_delay = CruiseControlManager.getCruiseClickDelay('CruiseActionTransitionBack')

    def _getCruiseObject(self):
        return self.Transition

    def _getCruisePosition(self, Object):
        ObjectEntity = Object.getEntity()
        HotSpot = ObjectEntity.getHotSpot()
        Position = HotSpot.getWorldPolygonCenter()
        return Position

    def _onAction(self):
        if GroupManager.hasObject("TransitionBack", "Point_Effect") is False:
            Trace.log("Manager", 0, "CruiseActionTransitionBack._onAction: "
                                    "group TransitionBack not found Point_Effect please add to psd")

        Point_Effect = GroupManager.getObject("TransitionBack", "Point_Effect")
        Position = Point_Effect.getPosition()

        if TaskManager.existTaskChain("CruiseActionTransitionBack") is True:
            TaskManager.cancelTaskChain("CruiseActionTransitionBack")
        with TaskManager.createTaskChain(Name="CruiseActionTransitionBack") as tc:
            tc.addTask("AliasCruiseControlAction", Position=Position, Object=Point_Effect)
            tc.addTask("TaskDelay", Time=self.click_delay)
            tc.addTask("TaskNotify", ID=Notificator.onCruiseActionEnd, Args=(self,))
