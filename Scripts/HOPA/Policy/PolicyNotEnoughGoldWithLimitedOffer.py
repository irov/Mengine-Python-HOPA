from Foundation.DemonManager import DemonManager
from Foundation.PolicyManager import PolicyManager
from Foundation.Systems.SystemMonetization import SystemMonetization
from Foundation.Task.TaskAlias import TaskAlias


class PolicyNotEnoughGoldWithLimitedOffer(TaskAlias):

    def _onParams(self, params):
        self.PageID = params.get("PageID")
        self.Descr = params.get("Descr")
        self.Gold = params.get("Gold")

    def _scopeDefaultAction(self, source):
        PolicyDefaultAction = PolicyManager.getPolicy("NotEnoughGoldMessage", "PolicyNotEnoughGoldDialog")
        source.addTask(PolicyDefaultAction, Gold=self.Gold, Descr=self.Descr, PageID=self.PageID)

    def _onGenerate(self, source):
        SpecialPromotion = DemonManager.getDemon("SpecialPromotion")
        LimitedPromo = DemonManager.getDemon("LimitedPromo")
        LimitedPromoProductID = LimitedPromo.getActivePromoNow()

        if LimitedPromoProductID is None:
            source.addScope(self._scopeDefaultAction)
            return

        source.addFunction(SpecialPromotion.run, LimitedPromoProductID)

        with source.addRaceTask(2) as (done, skip):
            done.addListener(Notificator.onPaySuccess, Filter=lambda prod_id: prod_id == LimitedPromoProductID)
            if self.Descr == "Hint":
                done.addTask("PolicyHintPlayPaid")

            skip.addEvent(SpecialPromotion.EVENT_WINDOW_CLOSE)  # wait until window closes
            skip.addScope(self._scopeDefaultAction)

        source.addFunction(PolicyManager.setPolicy, "NotEnoughGoldAction", None)
        source.addFunction(PolicyManager.setPolicy, "NotEnoughEnergyAction", None)
