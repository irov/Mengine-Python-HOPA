from Foundation.Notificator import Notificator
from Foundation.Task.MixinObjectTemplate import MixinTransition
from HOPA.CruiseAction import CruiseAction
from HOPA.CruiseControlManager import CruiseControlManager


class CruiseActionTransition(MixinTransition, CruiseAction):

    def _onCheck(self):
        return self.Transition.isActive()

    def _getCruiseObject(self):
        return self.Transition

    def _onAction(self, source):
        self.move_delay = CruiseControlManager.getCruiseMoveDelay('CruiseActionTransition')

        source.addDelay(self.move_delay)
        source.addTask("AliasCruiseControlAction",
                       Position=self.Transition.calcWorldHintPoint(), Object=self._getCruiseObject())
        source.addNotify(Notificator.onCruiseActionEnd, self)
