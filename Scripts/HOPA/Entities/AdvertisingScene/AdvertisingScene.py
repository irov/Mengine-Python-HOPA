from Foundation.Entity.BaseScopeEntity import BaseScopeEntity
from Foundation.TaskManager import TaskManager
from Foundation.SystemManager import SystemManager
from Foundation.SceneManager import SceneManager

class AdvertisingScene(BaseScopeEntity):
    def __init__(self):
        super(AdvertisingScene, self).__init__()
        self.prev_scene_name = None

    @staticmethod
    def declareORM(Type):
        BaseEntity.declareORM(Type)
        Type.addAction(Type, "AdvertSceneName")
        Type.addAction(Type, "CacheNoAds")

    def _onScopeActivate(self, source):
        source.addScope(self._scopeAds)

        # ---- to use this task, set Bypass to False at object.runNextTransition method
        # source.addTask("TaskTransitionUnblock", IsGameScene=False)
        source.addDelay(1)
        source.addFunction(self.object.runNextTransition)

        self.prev_scene_name = SceneManager.getPrevSceneName()

    def _onDeactivate(self):
        SceneManager.s_prevSceneName = self.prev_scene_name

    def _scopeAds(self, source):
        if self.object.getParam("CacheNoAds") is True:
            return

        SystemAdvertising = SystemManager.getSystem("SystemAdvertising")

        # did check ready early before activate (in AdvertScene object.runAdvertTransition)

        with source.addParallelTask(2) as (response, request):
            with response.addRaceTask(2) as (hidden, fail):
                hidden.addListener(Notificator.onAdvertHidden)
                fail.addListener(Notificator.onAdvertDisplayFailed)
            request.addFunction(SystemAdvertising.showInterstitial, descr="transition")
