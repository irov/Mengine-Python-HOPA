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
        source.addDummy()
        pass

    def _onScopeDeactivate(self):
        pass
