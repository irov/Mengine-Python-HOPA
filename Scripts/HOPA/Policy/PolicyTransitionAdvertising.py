from Foundation.Task.Task import Task
from Foundation.SystemManager import SystemManager
from Foundation.TaskManager import TaskManager
from Foundation.DemonManager import DemonManager

class PolicyTransitionAdvertising(Task):
    PLACEMENT = "transition"
    ADVERTISING_SCENE = "Advertising"

    def _onParams(self, params):
        self.TransitionData = params

    def _onRun(self):
        def __cbTransition(isSkip):
            self.complete(isSkiped=isSkip)
            pass

        if self.__checkAdInterstitial(self.TransitionData, PolicyTransitionAdvertising.PLACEMENT) is False:
            if Skip is False:
                TaskManager.runAlias("AliasTransition", __cbTransition, Bypass=True, **self.TransitionData)
                pass
            return False

        AdvertisingScene = DemonManager.getDemon("AdvertisingScene")
        AdvertisingScene.setParam("TransitionData", self.TransitionData)
        AdvertisingScene.setParam("Placement", PolicyTransitionAdvertising.PLACEMENT)

        AdvertisingTransitionData = dict(self.TransitionData, SceneName=PolicyTransitionAdvertising.ADVERTISING_SCENE)

        TaskManager.runAlias("AliasTransition", __cbTransition, **AdvertisingTransitionData)

        return False

