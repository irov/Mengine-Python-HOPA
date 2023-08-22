from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.TaskManager import TaskManager
from Foundation.SystemManager import SystemManager


class AdvertisingScene(BaseEntity):

    def __init__(self):
        super(AdvertisingScene, self).__init__()
        self.tc = None

    @staticmethod
    def declareORM(Type):
        BaseEntity.declareORM(Type)
        Type.addAction(Type, "AdvertSceneName")
        Type.addAction(Type, "CacheNoAds")

    def _onActivate(self):
        self.__runTaskChain()

    def _onDeactivate(self):
        if self.tc is not None:
            self.tc.cancel()
            self.tc = None

    def __runTaskChain(self):
        self.tc = TaskManager.createTaskChain()

        with self.tc as tc:
            tc.addScope(self._scopeAds)

            # ---- to use this task, set Bypass to False at object.runNextTransition method
            # tc.addTask("TaskTransitionUnblock", IsGameScene=False)
            tc.addDelay(1)

            tc.addFunction(self.object.runNextTransition)

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
