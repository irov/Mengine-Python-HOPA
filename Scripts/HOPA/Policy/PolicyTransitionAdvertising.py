from Foundation.Task.Task import Task
from Foundation.SystemManager import SystemManager
from Foundation.TaskManager import TaskManager
from Foundation.DemonManager import DemonManager
from Foundation.Providers.AdvertisementProvider import AdvertisementProvider

class PolicyTransitionAdvertising(Task):
    PLACEMENT = "transition"
    ADVERTISING_SCENE = "Advertising"
    IGNORE_SCENES = ["CutScene", "Dialog"]

    def _onParams(self, params):
        self.TransitionData = params

    def _onRun(self):
        def __cbTransition(isSkip):
            self.complete(isSkiped=isSkip)
            pass

        def __checkAdInterstitial(TransitionData, Placement):
            if TransitionData.get("SceneName") in PolicyTransitionAdvertising.IGNORE_SCENES:
                return False

            if Placement is None:
                return False

            if AdvertisementProvider.hasInterstitialAdvert() is False:
                return False

            if AdvertisementProvider.canYouShowInterstitialAdvert(Placement) is False:
                return False

            return True

        if __checkAdInterstitial(self.TransitionData, PolicyTransitionAdvertising.PLACEMENT) is False:
            TaskManager.runAlias("AliasTransition", __cbTransition, Bypass=True, **self.TransitionData)
            return False

        AdvertisingScene = DemonManager.getDemon("AdvertisingScene")
        AdvertisingScene.setParam("TransitionData", self.TransitionData)
        AdvertisingScene.setParam("Placement", PolicyTransitionAdvertising.PLACEMENT)

        AdvertisingTransitionData = dict(self.TransitionData, SceneName=PolicyTransitionAdvertising.ADVERTISING_SCENE)

        TaskManager.runAlias("AliasTransition", __cbTransition, **AdvertisingTransitionData)

        return False

