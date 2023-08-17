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
            tc.addDelay(1)  # necessary for transition
            tc.addFunction(self.object.runNextTransition)

    def _scopeAds(self, source):
        if self.object.getParam("CacheNoAds") is True:
            return

        SystemAdvertising = SystemManager.getSystem("SystemAdvertising")

        if SystemAdvertising.isDisabledForever() is True:
            self.object.setParam("CacheNoAds", True)
            return

        if SystemAdvertising.isReadyToView() is False:
            return

        with source.addParallelTask(2) as (response, request):
            with response.addRaceTask(2) as (hidden, fail):
                hidden.addListener(Notificator.onAdvertHidden)
                fail.addListener(Notificator.onAdvertDisplayFailed)
            request.addFunction(SystemAdvertising.showInterstitial, descr="transition")
