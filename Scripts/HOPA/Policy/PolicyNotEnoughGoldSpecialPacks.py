from Foundation.DemonManager import DemonManager
from Foundation.MonetizationManager import MonetizationManager
from Foundation.Systems.SystemMonetization import SystemMonetization
from HOPA.StoreManager import StoreManager
from Foundation.PolicyManager import PolicyManager
from Foundation.Task.TaskAlias import TaskAlias


COMPONENT_NAME = "TriggerSpecialPacks"


class PolicyNotEnoughGoldSpecialPacks(TaskAlias):

    def _onParams(self, params):
        self.PageID = params.get("PageID")
        self.Descr = params.get("Descr")
        self.Gold = params.get("Gold")

    def _onInitialize(self):
        if _DEVELOPMENT is True:
            component = MonetizationManager.getComponentType(COMPONENT_NAME)
            if component is None:
                self.initializeFailed("Not found required component {!r}".format(COMPONENT_NAME))

    def _onGenerate(self, source):
        SpecialPromotion = DemonManager.getDemon("SpecialPromotion")
        TriggerSpecialPacks = SystemMonetization.getComponent(COMPONENT_NAME)

        PolicyDefaultAction = PolicyManager.getPolicy("NotEnoughGoldMessage", "PolicyNotEnoughGoldDialog")
        PolicyOnSkipAction = PolicyManager.getPolicy("NotEnoughGoldOnSkipAction", PolicyDefaultAction)

        product_id = TriggerSpecialPacks.getPackProductId()
        page_id = self._findPageId(product_id)

        source.addFunction(TriggerSpecialPacks.showPack)

        with source.addRaceTask(3) as (done, skip, stop):
            done.addListener(Notificator.onPaySuccess)
            if MonetizationManager.getGeneralSetting("AllowPayGoldAfterPurchase", False) is True:
                done.addNotify(Notificator.onGameStorePayGold, descr=self.Descr)

            skip.addEvent(SpecialPromotion.EVENT_WINDOW_CLOSE)  # wait until window closes
            skip.addTask(PolicyOnSkipAction, Gold=self.Gold, Descr=self.Descr, PageID=page_id)

            stop.addListener(Notificator.onSceneDeactivate)
            # prevent pay with no results

    def _findPageId(self, product_id):
        product = MonetizationManager.getProductInfo(product_id)

        page_id = StoreManager.findPageIdByProductId(product.id)
        if page_id is None:
            page_id = StoreManager.findPageIdByProductId(product.alias_id)
            if page_id is None:
                page_id = self.PageID

        return page_id

