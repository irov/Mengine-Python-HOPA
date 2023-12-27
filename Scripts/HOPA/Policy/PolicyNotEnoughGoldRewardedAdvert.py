from Foundation.DemonManager import DemonManager
from Foundation.MonetizationManager import MonetizationManager
from Foundation.Systems.SystemMonetization import SystemMonetization
from Foundation.PolicyManager import PolicyManager
from Foundation.Task.TaskAlias import TaskAlias


class PolicyNotEnoughGoldRewardedAdvert(TaskAlias):

    def _scopeDefaultAction(self, source):
        PolicyDefaultAction = PolicyManager.getPolicy("NotEnoughGoldMessage", "PolicyNotEnoughGoldDialog")
        # PolicyOnSkipAction = PolicyManager.getPolicy("NotEnoughGoldOnSkipAction", PolicyDefaultAction)
        source.addTask(PolicyDefaultAction, Gold=self.Gold, Descr=self.Descr, PageID=self.PageID)

    def _onParams(self, params):
        self.PageID = params.get("PageID")
        self.Descr = params.get("Descr")
        self.Gold = params.get("Gold")

    def _onGenerate(self, source):
        SpecialPromotion = DemonManager.getDemon("SpecialPromotion")
        AdvertProduct = MonetizationManager.getGeneralProductInfo("AdvertNotEnoughMoneyProductID")

        if SystemMonetization.isAdsEnded(AdvertProduct.name) is True:
            source.addScope(self._scopeDefaultAction)
            return

        semaphore_rewarded_ok = Semaphore(False, "AdvertRewardedStatus")

        source.addFunction(SpecialPromotion.run, AdvertProduct.id)

        with source.addRaceTask(3) as (done, skip, stop):
            with done.addParallelTask(2) as (rewarded, hidden):
                rewarded.addListener(Notificator.onAdvertRewarded)
                rewarded.addSemaphore(semaphore_rewarded_ok, To=True)
                hidden.addListener(Notificator.onAdvertHidden)
            if MonetizationManager.getGeneralSetting("AllowPayGoldAfterPurchase", False) is True:
                done.addNotify(Notificator.onGameStorePayGold, descr=self.Descr)

            skip.addEvent(SpecialPromotion.EVENT_WINDOW_CLOSE)  # wait until window closes
            skip.addDelay(100)
            skip.addSemaphore(semaphore_rewarded_ok, From=False)
            skip.addScope(self._scopeDefaultAction)

            stop.addListener(Notificator.onSceneDeactivate)
