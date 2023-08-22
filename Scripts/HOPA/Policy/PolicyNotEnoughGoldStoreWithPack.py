from Foundation.DemonManager import DemonManager
from Foundation.MonetizationManager import MonetizationManager
from Foundation.PolicyManager import PolicyManager
from Foundation.Task.TaskAlias import TaskAlias


class PolicyNotEnoughGoldStoreWithPack(TaskAlias):

    def _onParams(self, params):
        self.PageID = params.get("PageID")
        self.Descr = params.get("Descr")
        self.Gold = params.get("Gold")

    def _onGenerate(self, source):
        SpecialPromotion = DemonManager.getDemon("SpecialPromotion")
        PromoPackageProduct = MonetizationManager.getGeneralProductInfo("PromoPackageProductID")

        PolicyDefaultAction = PolicyManager.getPolicy("NotEnoughGoldMessage", "PolicyNotEnoughGoldDialog")
        PolicyOnSkipAction = PolicyManager.getPolicy("NotEnoughGoldOnSkipAction", PolicyDefaultAction)

        source.addFunction(SpecialPromotion.run, PromoPackageProduct.id)

        with source.addRaceTask(3) as (done, skip, stop):
            done.addListener(Notificator.onPaySuccess)
            if MonetizationManager.getGeneralSetting("AllowPayGoldAfterPurchase", False) is True:
                done.addNotify(Notificator.onGameStorePayGold, descr=self.Descr)

            skip.addEvent(SpecialPromotion.EVENT_WINDOW_CLOSE)  # wait until window closes
            skip.addTask(PolicyOnSkipAction, Gold=self.Gold, Descr=self.Descr, PageID=self.PageID)

            stop.addListener(Notificator.onSceneDeactivate)
            # prevent pay with no results
