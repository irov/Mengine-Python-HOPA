from Foundation.Task.Task import Task
from Foundation.SystemManager import SystemManager

class PolicyTransitionAdvertising(Task):
    def _onParams(self, params):
        self.TransitionData = params

    def _onRun(self):
        Trace.msg_dev("PolicyTransitionAdvertising", self.TransitionData)

        SystemAdvertising = SystemManager.getSystem("SystemAdvertising")

        SystemAdvertising.tryInterstitial(self.TransitionData, "transition", self._cbTransition)

        return False

    def _cbTransition(self, isSkip):
        self.complete(isSkiped=isSkip)

