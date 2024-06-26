from Foundation.DemonManager import DemonManager
from Foundation.MonetizationManager import MonetizationManager
from Foundation.PolicyManager import PolicyManager
from Foundation.Task.TaskAlias import TaskAlias


class PolicyNotEnoughEnergyStoreWithPack(TaskAlias):

    def _onParams(self, params):
        self.Action = params.get("Action")
        self.PageID = params.get("PageID")
        self.Amount = params.get("Amount")

    def _onGenerate(self, source):
        SpecialPromotion = DemonManager.getDemon("SpecialPromotion")
        PromoPackageProduct = MonetizationManager.getGeneralProductInfo("PromoPackageProductID")

        PolicyDefaultAction = PolicyManager.getPolicy("NotEnoughEnergyMessage", "PolicyNotEnoughEnergyDialog")
        PolicyOnSkipAction = PolicyManager.getPolicy("NotEnoughEnergyOnSkipAction", PolicyDefaultAction)

        source.addFunction(SpecialPromotion.run, PromoPackageProduct.id)

        with source.addRaceTask(2) as (done, skip):
            done.addListener(Notificator.onPaySuccess)

            skip.addEvent(SpecialPromotion.EVENT_WINDOW_CLOSE)  # wait until window closes
            skip.addTask(PolicyOnSkipAction, PageID=self.PageID, Action=self.Action, Amount=self.Amount)
