from Foundation.MonetizationManager import MonetizationManager
from Foundation.PolicyManager import PolicyManager
from HOPA.Entities.Monetization.BaseComponent import BaseComponent

POLICY_GOLD_NAME = "NotEnoughGoldOnSkipAction"
POLICY_ENERGY_NAME = "NotEnoughEnergyOnSkipAction"


class AdvertNotEnoughMoney(BaseComponent):
    _settings = {
        "product_id": "AdvertNotEnoughMoneyProductID",
        "is_enable": "AdvertNotEnoughMoneyEnable",
    }
    _defaults = {
        "is_enable": False
    }

    def _check(self):
        if self.product is None:
            self._error("Not found product with id {!r} [{}]".format(self._product_lookup_id, self._settings["product_id"]))
            return False
        if MonetizationManager.getSpecialPromoById(self.product.id) is None:
            self._error("Not found SpecialPromotion with id {!r}".format(self.product.id))
            return False
        return True

    def _run(self):
        self.addObserver(Notificator.onAvailableAdsEnded, self._onAvailableAdsEnded)
        self.addObserver(Notificator.onAvailableAdsNew, self._onAvailableAdsNew)

        self._setPolicy()
        return True

    def _setPolicy(self):
        if "Gold" in self.product.reward:
            PolicyManager.setPolicy(POLICY_GOLD_NAME, "PolicyNotEnoughGoldRewardedAdvert")
        if "Energy" in self.product.reward:
            PolicyManager.setPolicy(POLICY_ENERGY_NAME, "PolicyNotEnoughEnergyRewardedAdvert")

    def _onAvailableAdsEnded(self, ad_name):
        if self.product.name == ad_name:
            PolicyManager.delPolicy(POLICY_GOLD_NAME)
            PolicyManager.delPolicy(POLICY_ENERGY_NAME)

    def _onAvailableAdsNew(self, ad_name):
        if self.product.name == ad_name:
            self._setPolicy()

