from Foundation.DemonManager import DemonManager
from Foundation.MonetizationManager import MonetizationManager
from Foundation.PolicyManager import PolicyManager
from Foundation.Systems.SystemMonetization import SystemMonetization
from HOPA.Entities.Monetization.BaseComponent import BaseComponent


class PromoPackageNotEnoughMoney(BaseComponent):
    _settings = {
        "product_id": "PromoPackageProductID",
        "is_enable": "PromoPackageNotEnoughMoney",
    }
    _defaults = {
        "is_enable": False
    }

    def _check(self):
        if self.product is None:
            self._error("Not found product with id {!r}".format(self._product_lookup_id))
            return False
        if MonetizationManager.getSpecialPromoById(self.product.id) is None:
            self._error("Not found SpecialPromotion with id {!r}".format(self.product.id))
            return False
        for demon_name in ["DialogWindow", "SpecialPromotion", SystemMonetization.game_store_name]:
            if DemonManager.hasDemon(demon_name) is False:
                self._error("Demon {!r} is not active".format(demon_name))
                return False
        return True

    def _run(self):
        self.addObserver(Notificator.onSelectAccount, self._cbSelectAccount)
        self.addObserver(Notificator.onPaySuccess, self._cbPaySuccess)
        return True

    def _cbSelectAccount(self, account_id):
        if SystemMonetization.isProductPurchased(self.product.id) is False:
            PolicyManager.setPolicy("NotEnoughGoldAction", "PolicyNotEnoughGoldStoreWithPack")
            PolicyManager.setPolicy("NotEnoughEnergyAction", "PolicyNotEnoughEnergyStoreWithPack")
        return False

    def _cbPaySuccess(self, prod_id):
        if prod_id != self.getProductId():
            return False

        if PolicyManager.getPolicy("NotEnoughGoldAction") == "PolicyNotEnoughGoldStoreWithPack":
            PolicyManager.setPolicy("NotEnoughGoldAction", None)
        if PolicyManager.getPolicy("NotEnoughEnergyAction") == "PolicyNotEnoughEnergyStoreWithPack":
            PolicyManager.setPolicy("NotEnoughEnergyAction", None)

        return False
