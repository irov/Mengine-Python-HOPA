from Foundation.SystemManager import SystemManager
from HOPA.MonetizationManager import MonetizationManager


ACTION_PURCHASE = MonetizationManager.SpecialPromoParam.ACTIONS[0]
ACTION_ADVERT = MonetizationManager.SpecialPromoParam.ACTIONS[1]


class PurchaseButton(object):

    def __init__(self, movie, action_name):
        self.movie = movie
        self.action = action_name

    def getEntityNode(self):
        return self.movie.getEntityNode()

    def setEnable(self, state):
        self.movie.setEnable(bool(state))

    def cleanUp(self):
        self.action = None
        self.movie.removeFromParent()
        self.movie.onDestroy()
        self.movie = None

    def scopeClick(self, source):
        source.addTask("TaskMovie2ButtonClick", Movie2Button=self.movie)

    def scopeActivate(self, source, product_id, scopeSuccess):
        if self.action == ACTION_PURCHASE:
            SystemMonetization = SystemManager.getSystem("SystemMonetization")
            source.addScope(SystemMonetization.scopePay, product_id, scopeSuccess=scopeSuccess)
        elif self.action == ACTION_ADVERT:
            source.addTask("AliasShowAdvert", AdType="Rewarded", SuccessCallback=Functor(source.addScope, scopeSuccess))


class DeprecatedPurchaseButton(PurchaseButton):
    def cleanUp(self):
        self.action = None
        self.movie.returnToParent()
        self.movie = None
