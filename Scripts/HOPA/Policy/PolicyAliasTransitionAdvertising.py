from Foundation.Task.TaskAlias import TaskAlias
from Foundation.SceneManager import SceneManager
from Foundation.Providers.AdvertisementProvider import AdvertisementProvider

class PolicyAliasTransitionAdvertising(TaskAlias):
    PLACEMENT = "transition"
    ADVERTISING_SCENE = "Advertising"
    IGNORE_SCENES = ["CutScene", "Dialog"]

    def _onParams(self, params):
        super(PolicyAliasTransitionAdvertising, self)._onParams(params)
        self.SceneName=params.get("SceneName")
        self.Wait=params.get("Wait")
        self.SkipTaskChains=params.get("SkipTaskChains")
        self.CheckToScene=params.get("CheckToScene", True)
        pass

    def _onGenerate(self, source):
        def __checkAdInterstitial():
            if self.SceneName in PolicyAliasTransitionAdvertising.IGNORE_SCENES:
                return False

            if SceneManager.isGameScene(self.SceneName) is False:
                return False

            if AdvertisementProvider.hasInterstitialAdvert() is False:
                return False

            if AdvertisementProvider.canYouShowInterstitialAdvert(PolicyAliasTransitionAdvertising.PLACEMENT) is False:
                return False

            return True

        if __checkAdInterstitial() is False:
            source.addPrint("[AD] No advert: {}".format(self.SceneName))
            source.addTask("TaskTransition", SceneName=self.SceneName, Wait=self.Wait, SkipTaskChains=self.SkipTaskChains, CheckToScene=self.CheckToScene)
            return

        source.addTask("TaskTransition", SceneName=PolicyAliasTransitionAdvertising.ADVERTISING_SCENE, Wait=self.Wait, SkipTaskChains=self.SkipTaskChains, CheckToScene=self.CheckToScene)
        with source.addRaceTask(2) as (response, request):
            response.addListener(Notificator.onAdShowCompleted)
            response.addPrint("[AD] Ad finished: {} ".format(self.SceneName))
            def __showInterstitialAdvert():
                return AdvertisementProvider.showInterstitialAdvert(PolicyAliasTransitionAdvertising.PLACEMENT)
            with request.addIfTask(__showInterstitialAdvert) as (show, skip):
                show.addPrint("[AD] Showing advert: {}".format(self.SceneName))
                show.addBlock()
                skip.addPrint("[AD] Skip advert: {}".format(self.SceneName))
                pass
        source.addPrint("[AD] Continue transition: {} ".format(self.SceneName))
        source.addDelay(1)
        source.addTask("TaskTransition", SceneName=self.SceneName, Wait=self.Wait, SkipTaskChains=self.SkipTaskChains, CheckToScene=self.CheckToScene)
        pass
    pass
