from Foundation.DemonManager import DemonManager
from Foundation.MonetizationManager import MonetizationManager
from Foundation.Systems.SystemMonetization import SystemMonetization
from Foundation.TaskManager import TaskManager
from HOPA.Entities.Monetization.BaseComponent import BaseComponent


TC_NAME = "SpecialPackageDisableAds"


class DisableAds(BaseComponent):
    _settings = {
        "product_id": "DisableAdsProductId",
    }
    _defaults = {
        "product_id": "disable_ads",
        "is_enable": True
    }

    def _createParams(self):
        self.tc = None
        self.demon_name = "SpecialPromotion"
        self.demon = DemonManager.getDemon(self.demon_name) if DemonManager.hasDemon(self.demon_name) else None

    def _check(self):
        if self.product is None:
            return False
        if self.demon is None:
            self._error("Demon '{}' not found".format(self.demon_name))
            return False
        if MonetizationManager.getSpecialPromoById(self.product.id) is None:
            self._error("Not found SpecialPromotion with id {!r}".format(self.product.id))
            return False
        return True

    def _initialize(self):
        return True

    def _run(self):
        self.addObserver(Notificator.onSelectAccount, self._cbSelectAccount)
        return True

    def _cbSelectAccount(self, account_id):
        if TaskManager.existTaskChain(TC_NAME):
            TaskManager.cancelTaskChain(TC_NAME)

        if SystemMonetization.isProductPurchased(self.product.id) is True:
            return False

        with TaskManager.createTaskChain(Name=TC_NAME) as tc:
            with tc.addRepeatTask() as (repeat, until):
                repeat.addListener(Notificator.onAdvertHidden, Filter=lambda ad_type, ad_name: ad_type == "Interstitial")
                repeat.addFunction(self.demon.run, self.product.id)

                until.addListener(Notificator.onPaySuccess, Filter=lambda prod_id: prod_id == self.product.id)

        return False

    def _cleanUp(self):
        if TaskManager.existTaskChain(TC_NAME):
            TaskManager.cancelTaskChain(TC_NAME)
