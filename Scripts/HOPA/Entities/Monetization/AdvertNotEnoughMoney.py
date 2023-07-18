from Foundation.MonetizationManager import MonetizationManager
from Foundation.PolicyManager import PolicyManager
from HOPA.Entities.Monetization.BaseComponent import BaseComponent


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
        if "Gold" in self.product.reward:
            PolicyManager.setPolicy("NotEnoughGoldOnSkipAction", "PolicyNotEnoughGoldRewardedAdvert")
        if "Energy" in self.product.reward:
            PolicyManager.setPolicy("NotEnoughEnergyOnSkipAction", "PolicyNotEnoughEnergyRewardedAdvert")
        return True

