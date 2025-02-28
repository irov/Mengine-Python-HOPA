from Foundation.Notificator import Notificator
from Foundation.Task.MixinGroup import MixinGroup
from Foundation.TaskManager import TaskManager

from HOPA.CruiseAction import CruiseAction


class CruiseActionDefault(MixinGroup, CruiseAction):

    def _onInitialize(self):
        super(CruiseActionDefault, self)._onInitialize()

        self.hintObject = self._getCruiseObject()

    def _onAction(self):
        PositionTo = self._getCruisePosition(self.hintObject)

        if TaskManager.existTaskChain("CruiseActionDefault"):
            TaskManager.cancelTaskChain("CruiseActionDefault")

        with TaskManager.createTaskChain(Name="CruiseActionDefault") as tc:
            tc.addTask("AliasCruiseControlAction", Position=PositionTo, Object=self.hintObject)
            tc.addNotify(Notificator.onCruiseActionEnd, self)

    def _getCruiseObject(self):
        Trace.msg_err("CruiseActionDefault - Invalid Cruise Object")
        return None

    def _getCruisePosition(self, Object):
        Trace.msg_err("CruiseActionDefault - Invalid Cruise Position {}".format(Object))
        return 0, 0

    def _onEnd(self):
        if TaskManager.existTaskChain("CruiseActionDefault"):
            TaskManager.cancelTaskChain("CruiseActionDefault")
