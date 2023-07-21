from Foundation.DemonManager import DemonManager
from Foundation.MonetizationManager import MonetizationManager
from Foundation.Systems.SystemMonetization import SystemMonetization
from Foundation.PolicyManager import PolicyManager
from Foundation.Task.TaskAlias import TaskAlias


class PolicyNotEnoughEnergyRewardedAdvert(TaskAlias):

    def _scopeDefaultAction(self, source):
        PolicyDefaultAction = PolicyManager.getPolicy("NotEnoughEnergyMessage", "PolicyNotEnoughEnergyDialog")
        # PolicyOnSkipAction = PolicyManager.getPolicy("NotEnoughEnergyOnSkipAction", PolicyDefaultAction)
        source.addTask(PolicyDefaultAction, Action=self.Action, PageID=self.PageID)

    def _onParams(self, params):
        self.Action = params.get("Action")
        self.PageID = params.get("PageID")

    def _onGenerate(self, source):
        SpecialPromotion = DemonManager.getDemon("SpecialPromotion")
        AdvertProduct = MonetizationManager.getGeneralProductInfo("AdvertNotEnoughMoneyProductID")

        if SystemMonetization.isAdsEnded() is True:
            source.addScope(self._scopeDefaultAction)
            return

        source.addFunction(SpecialPromotion.run, AdvertProduct.id)

        with source.addRaceTask(3) as (done, skip, stop):
            done.addListener(Notificator.onAdvertHidden)

            skip.addEvent(SpecialPromotion.EVENT_WINDOW_CLOSE)  # wait until window closes
            skip.addScope(self._scopeDefaultAction)

            stop.addListener(Notificator.onSceneDeactivate)
