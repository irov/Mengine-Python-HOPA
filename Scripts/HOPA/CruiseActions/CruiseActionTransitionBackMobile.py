from Foundation.Task.MixinObjectTemplate import MixinTransition
from Foundation.TaskManager import TaskManager
from HOPA.CruiseActions.CruiseActionDefault import CruiseActionDefault
from HOPA.CruiseControlManager import CruiseControlManager
from HOPA.System.SystemNavigation import SystemNavigation

class CruiseActionTransitionBackMobile(MixinTransition, CruiseActionDefault):

    def _onParams(self, params):
        super(CruiseActionTransitionBackMobile, self)._onParams(params)
        self.click_delay = CruiseControlManager.getCruiseClickDelay('CruiseActionTransitionBackMobile', 500)
        self.Transition = SystemNavigation.getNavGoBackButton()

    def _getCruiseObject(self):
        return self.Transition

    def _getCruisePosition(self, object):
        entity = object.getEntity()
        position = entity.getCurrentMovieSocketCenter()
        return position

    def _onAction(self):
        transition = self._getCruiseObject()
        position = self._getCruisePosition(transition)

        if TaskManager.existTaskChain("CruiseActionTransitionBackMobile") is True:
            TaskManager.cancelTaskChain("CruiseActionTransitionBackMobile")
        with TaskManager.createTaskChain(Name="CruiseActionTransitionBackMobile") as tc:
            tc.addTask("AliasCruiseControlAction", Position=position, Object=transition)
            tc.addDelay(self.click_delay)
            tc.addNotify(Notificator.onCruiseActionEnd, self)