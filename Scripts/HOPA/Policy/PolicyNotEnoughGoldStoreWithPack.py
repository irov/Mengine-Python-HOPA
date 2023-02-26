from Foundation.DemonManager import DemonManager
from Foundation.MonetizationManager import MonetizationManager
from Foundation.PolicyManager import PolicyManager
from Foundation.Systems.SystemMonetization import SystemMonetization
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

        source.addFunction(SpecialPromotion.run, PromoPackageProduct.id)

        with source.addRaceTask(2) as (done, skip):
            done.addListener(Notificator.onPaySuccess)
            done.addFunction(PolicyManager.setPolicy, "NotEnoughGoldAction", None)
            done.addFunction(PolicyManager.setPolicy, "NotEnoughEnergyAction", None)
            done.addFunction(SystemMonetization.payGold, descr=self.Descr)

            skip.addEvent(SpecialPromotion.EVENT_WINDOW_CLOSE)  # wait until window closes
            skip.addTask(PolicyDefaultAction, Gold=self.Gold, Descr=self.Descr, PageID=self.PageID)