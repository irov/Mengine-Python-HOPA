from Foundation.DemonManager import DemonManager
from Foundation.GroupManager import GroupManager
from Foundation.MonetizationManager import MonetizationManager
from Foundation.SystemManager import SystemManager
from Foundation.Task.TaskAlias import TaskAlias
from Foundation.Utils import getCurrentPublisher


class PolicyGuideOpenPaid(TaskAlias):

    def _onParams(self, params):
        super(PolicyGuideOpenPaid, self)._onParams(params)

        self.ButtonName = params.get("Movie2ButtonName")
        if self.ButtonName is None:
            publisher = getCurrentPublisher()
            button_name = MonetizationManager.getGeneralSetting("GuidesButton", "Movie2Button_{}".format(publisher))
            if GroupManager.hasObject(self.GroupName, button_name) is False:
                button_name = "Movie2Button_Guide"  # default
            self.ButtonName = button_name

        self.ProdParams = MonetizationManager.getGeneralProductInfo("GuidesProductID")

        if MonetizationManager.getGeneralSetting("GameStoreName", "GameStore") == "Store":
            self._variant = "Store"
            self.PageID = MonetizationManager.getGeneralSetting("GuidesPageID")
        else:
            self._variant = "SpecialPromotion"

    def _scopeTransition(self, source):
        source.addNotify(Notificator.onBonusSceneTransition, "Guide")

    def _scopeSpecialPromotion(self, source):
        """ _variant = "SpecialPromotion" """
        SpecialPromotion = DemonManager.getDemon("SpecialPromotion")

        source.addFunction(SpecialPromotion.run, self.ProdParams.id)
        source.addEvent(SpecialPromotion.EVENT_WINDOW_CLOSE)  # wait until window closes

    def _scopeStorePage(self, source):
        """ _variant = "Store" """

        SystemStore = SystemManager.getSystem("SystemStore")
        Store = DemonManager.getDemon("Store")
        GuidePageID = self.PageID

        SystemStore.setCurrentPageID(GuidePageID)
        Store.open()

        with source.addRaceTask(2) as (purchase, leave):
            purchase.addListener(Notificator.onPaySuccess, Filter=lambda prod_id: prod_id == self.ProdParams.id)
            leave.addListener(Notificator.onSceneDeactivate, Filter=lambda scene_name: scene_name == "Store")

    def _onGenerate(self, source):
        SystemMonetization = SystemManager.getSystem("SystemMonetization")

        source.addTask("TaskMovie2ButtonClick", GroupName=self.GroupName, Movie2ButtonName=self.ButtonName)

        with source.addIfTask(SystemMonetization.isProductPurchased, self.ProdParams.id) as (show, purchase):
            show.addScope(self._scopeTransition)

            # ---- this part immediately activate delayed purchase -----------------------------------------------------
            # if SystemMonetization.isPurchaseDelayed(self.ProdParams.id) is True:
            #     with purchase.addParallelTask(2) as (purchased, release):
            #         purchased.addListener(Notificator.onPaySuccess, Filter=lambda prod_id: prod_id == self.ProdParams.id)
            #         release.addNotify(Notificator.onReleasePurchased, self.ProdParams.id)
            # else:
            # ----------------------------------------------------------------------------------------------------------

            if self._variant == "SpecialPromotion":
                purchase.addScope(self._scopeSpecialPromotion)
            elif self._variant == "Store":
                purchase.addScope(self._scopeStorePage)
            else:
                Trace.log("Task", 0, "PolicyGuideOpenPaid unknown purchase variant {!r}".format(self._variant))

            with purchase.addIfTask(SystemMonetization.isProductPurchased, self.ProdParams.id) as (transition, fail):
                transition.addScope(self._scopeTransition)
