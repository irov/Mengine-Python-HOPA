from Foundation.SystemManager import SystemManager
from HOPA.MonetizationManager import MonetizationManager


ACTION_PURCHASE = MonetizationManager.SpecialPromoParam.ACTIONS[0]
ACTION_ADVERT = MonetizationManager.SpecialPromoParam.ACTIONS[1]


class PurchaseButton(object):

    def __init__(self, movie, action_name):
        self.movie = movie
        self.action = action_name
        self.product = None

    def getEntityNode(self):
        return self.movie.getEntityNode()

    def setEnable(self, state):
        self.movie.setEnable(bool(state))

    def setParams(self, params):
        self.product = MonetizationManager.getProductInfo(params.id)

        if self.action == ACTION_ADVERT:
            self.movie.setTextAliasEnvironment(self.product.name)

    def cleanUp(self):
        self.action = None
        self.movie.removeFromParent()
        self.movie.onDestroy()
        self.movie = None

    def scopeClick(self, source):
        source.addTask("TaskMovie2ButtonClick", Movie2Button=self.movie)

    def scopeActivate(self, source, scopeSuccess):
        if self.action == ACTION_PURCHASE:
            source.addScope(self._activatePurchase, scopeSuccess)
        elif self.action == ACTION_ADVERT:
            source.addScope(self._activateAdvert, scopeSuccess)

    def _activatePurchase(self, source, scopeSuccess):
        SystemMonetization = SystemManager.getSystem("SystemMonetization")
        source.addScope(SystemMonetization.scopePay, self.product.id, scopeSuccess=scopeSuccess)

    def _activateAdvert(self, source, scopeSuccess):
        semaphore_rewarded_ok = Semaphore(False, "AdvertRewardedStatus")

        def _scopeWhileView(src):
            with src.addRaceTask(2) as (ok, skip):
                ok.addListener(Notificator.onAdvertRewarded, Filter=lambda name, *_: name == self.product.name)
                ok.addSemaphore(semaphore_rewarded_ok, To=True)
                skip.addListener(Notificator.onAdvertSkipped, Filter=lambda _, ad_name: ad_name == self.product.name)

        source.addTask("AliasShowAdvert", AdType="Rewarded",
                       AdUnitName=self.product.name, WhileShowScope=_scopeWhileView)

        # wait until alias done (when ad hidden), then call success scope
        with source.addIfSemaphore(semaphore_rewarded_ok, True) as (tc_was_rewarded, tc_not_rewarded):
            tc_was_rewarded.addScope(scopeSuccess)


class DeprecatedPurchaseButton(PurchaseButton):
    def cleanUp(self):
        self.action = None
        self.movie.returnToParent()
        self.movie.setEnable(False)
        self.movie = None
