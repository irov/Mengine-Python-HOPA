from Foundation.DemonManager import DemonManager
from Foundation.PolicyManager import PolicyManager
from Foundation.Task.TaskAlias import TaskAlias


class PolicyNotEnoughEnergyWithLimitedOffer(TaskAlias):

    def _onParams(self, params):
        self.Action = params.get("Action")
        self.PageID = params.get("PageID")
        self.Amount = params.get("Amount")

    def _scopeDefaultAction(self, source):
        PolicyDefaultAction = PolicyManager.getPolicy("NotEnoughEnergyMessage", "PolicyNotEnoughEnergyDialog")
        PolicyOnSkipAction = PolicyManager.getPolicy("NotEnoughEnergyOnSkipAction", PolicyDefaultAction)
        source.addTask(PolicyOnSkipAction, Action=self.Action, PageID=self.PageID, Amount=self.Amount)

    def _onGenerate(self, source):
        SpecialPromotion = DemonManager.getDemon("SpecialPromotion")
        LimitedPromo = DemonManager.getDemon("LimitedPromo")
        LimitedPromoProductID = LimitedPromo.getActivePromoNow()

        if LimitedPromoProductID is None:
            source.addScope(self._scopeDefaultAction)
            return

        source.addFunction(SpecialPromotion.run, LimitedPromoProductID)

        with source.addRaceTask(2) as (done, skip):
            done.addListener(Notificator.onPaySuccess)

            skip.addEvent(SpecialPromotion.EVENT_WINDOW_CLOSE)  # wait until window closes
            skip.addScope(self._scopeDefaultAction)

        source.addFunction(PolicyManager.setPolicy, "NotEnoughGoldAction", None)
        source.addFunction(PolicyManager.setPolicy, "NotEnoughEnergyAction", None)
