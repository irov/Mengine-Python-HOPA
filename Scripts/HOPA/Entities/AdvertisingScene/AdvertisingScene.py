from Foundation.Entity.BaseScopeEntity import BaseScopeEntity
from Foundation.Providers.AdvertisementProvider import AdvertisementProvider

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
        source.addTask("AliasTransition", Bypass=True, **self.TransitionData)
