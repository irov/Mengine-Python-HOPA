from Foundation.DemonManager import DemonManager
from Foundation.MonetizationManager import MonetizationManager
from Foundation.Systems.SystemMonetization import SystemMonetization
from Foundation.PolicyManager import PolicyManager
from Foundation.Task.TaskAlias import TaskAlias


class PolicyNotEnoughGoldRewardedAdvert(TaskAlias):

    def _scopeDefaultAction(self, source):
        PolicyDefaultAction = PolicyManager.getPolicy("NotEnoughGoldMessage", "PolicyNotEnoughGoldDialog")
        PolicyOnSkipAction = PolicyManager.getPolicy("NotEnoughGoldOnSkipAction", PolicyDefaultAction)
        source.addTask(PolicyOnSkipAction, Gold=self.Gold, Descr=self.Descr, PageID=self.PageID)

    def _onParams(self, params):
        self.PageID = params.get("PageID")
        self.Descr = params.get("Descr")
        self.Gold = params.get("Gold")

    def _onGenerate(self, source):
        SpecialPromotion = DemonManager.getDemon("SpecialPromotion")
        AdvertProduct = MonetizationManager.getGeneralProductInfo("AdvertProductID")

        if SystemMonetization.isAdsEnded() is True:
            source.addScope(self._scopeDefaultAction)
            return

        source.addFunction(SpecialPromotion.run, AdvertProduct.id)

        with source.addRaceTask(3) as (done, skip, stop):
            done.addListener(Notificator.onAdvertHidden)
            done.addNotify(Notificator.onGameStorePayGold, descr=self.Descr)

            skip.addEvent(SpecialPromotion.EVENT_WINDOW_CLOSE)  # wait until window closes
            skip.addScope(self._scopeDefaultAction)

            stop.addListener(Notificator.onSceneDeactivate)