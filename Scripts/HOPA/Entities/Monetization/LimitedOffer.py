from Foundation.DemonManager import DemonManager
from Foundation.MonetizationManager import MonetizationManager
from Foundation.PolicyManager import PolicyManager
from Foundation.Systems.SystemMonetization import SystemMonetization
from HOPA.Entities.Monetization.BaseComponent import BaseComponent

"""
    Doc: https://wonderland-games.atlassian.net/wiki/spaces/SCR/pages/1897037829/LimitedPromo
"""

class LimitedOffer(BaseComponent):

    def _createParams(self):
        special_promotions = MonetizationManager.getSpecialPromotionParams()
        self.limited_promos = [promo for promo in special_promotions.values() if promo.limit_delay is not None]
        self.enable = len(self.limited_promos) != 0
        self.demon_name = "LimitedPromo"
        self.demon = DemonManager.getDemon(self.demon_name) if DemonManager.hasDemon(self.demon_name) else None

    def _check(self):
        if DemonManager.hasDemon("SpecialPromotion") is False:
            self._error("Not found demon 'SpecialPromotion'")
            return False
        if self.demon is None:
            self._error("Not found demon '{}'".format(self.demon_name))
            return False
        return True

    def _run(self):
        self.addObserver(Notificator.onSelectAccount, self._cbSelectAccount)
        self.addObserver(Notificator.onGameStoreNotEnoughGold, self._cbOfferLimitedPack)
        PolicyManager.setPolicy("NotEnoughGoldAction", "PolicyNotEnoughGoldWithLimitedOffer")
        PolicyManager.setPolicy("NotEnoughEnergyAction", "PolicyNotEnoughEnergyWithLimitedOffer")

    def _cbSelectAccount(self, account_id):
        self._actualizePromos()
        return False

    def _actualizePromos(self):
        for promo in self.limited_promos:
            product = MonetizationManager.getProductInfo(promo.id)

            if product.only_one_purchase is False:
                continue

            if SystemMonetization.isProductPurchased(product.id) is True:
                self.demon.endPromoByProductId(product.id)

    def isAvailablePromo(self, promo):
        product = MonetizationManager.getProductInfo(promo.id)

        if product.only_one_purchase is True and SystemMonetization.isProductPurchased(product.id) is True:
            # product already purchased and never could be run
            return False

        if self.demon.isActivated(product.id) is True:
            # product was activated early

            if promo.offer_delay is not None:
                # can we activate this promotion again now?

                activate_timestamp = self.demon.whenActivated(product.id)
                if (Mengine.getTimeMs() / 1000 - activate_timestamp) < promo.offer_delay:
                    return False

        return True

    def _cbOfferLimitedPack(self, *args):
        """ If player has not enough gold to purchase, we try to offer special limited product.
            Player could purchase it only once, if product `only_one_purchase` flag is True.
            If SpecialPromotion has `offer_delay`, then limited offer could not start, if delay not ended """

        if self.demon.hasActivePromo() is True:
            return False

        for promo in self.limited_promos:
            if self.isAvailablePromo(promo) is False:
                continue

            self.demon.run(promo.id)
            return False

        return False