from Foundation.Entity.BaseScopeEntity import BaseScopeEntity
from Foundation.Providers.AdvertisementProvider import AdvertisementProvider
from Foundation.TaskManager import TaskManager
from Foundation.SceneManager import SceneManager

class AdvertisingScene(BaseScopeEntity):
    @staticmethod
    def declareORM(Type):
        BaseScopeEntity.declareORM(Type)
        Type.addAction(Type, "TransitionData")
        Type.addAction(Type, "Placement")

    def _onPreparation(self):
        if _DEVELOPMENT is True and self.object.hasObject("Movie2_Content"):
            movie = self.object.getObject("Movie2_Content")
            movie.setEnable(True)

    def _onScopeActivate(self, source):
        self.prev_scene_name = SceneManager.getPrevSceneName()

        with source.addRaceTask(2) as (response, request):
            response.addListener(Notificator.onAdShowCompleted)
            response.addPrint("[AD] Ad finished")
            def __showInterstitialAdvert():
                return AdvertisementProvider.showInterstitialAdvert(self.Placement)
            with request.addIfTask(__showInterstitialAdvert) as (show, skip):
                show.addPrint("[AD] Showing advert")
                show.addBlock()
                skip.addPrint("[AD] Skip advert")
        source.addPrint("[AD] Continue transition: {} ".format(self.TransitionData))
        source.addDelay(1)

        def __transition():
            AdvertisingTransitionData = dict(SceneName=self.TransitionData.get("SceneName")
                                             , ZoomGroupName=self.TransitionData.get("ZoomGroupName")
                                             , MovieOut=self.TransitionData.get("MovieOut")
                                             , ZoomEffectTransitionBackObject=self.TransitionData.get("ZoomEffectTransitionBackObject"))

            #AdvertisingTransitionData = dict(SceneName=self.TransitionData.get("SceneName"))
            TaskManager.runAlias("AliasTransition", None, Bypass=True, **AdvertisingTransitionData)
            pass

        source.addFunction(__transition)
        #source.addTask("AliasTransition", Bypass=True, **AdvertisingTransitionData)

    def _onScopeDeactivate(self):
        SceneManager.s_prevSceneName = self.prev_scene_name
        pass
