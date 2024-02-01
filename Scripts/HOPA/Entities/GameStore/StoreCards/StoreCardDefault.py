from Foundation.MonetizationManager import MonetizationManager
from Foundation.SystemManager import SystemManager
from HOPA.Entities.GameStore.StoreCards.StoreCardMixin import StoreCardMixin


class StoreCardDefault(StoreCardMixin):
    # PRICE_TEMPLATE is overrides in GameStore.createStoreCards
    PRICE_TEMPLATE = "{currency}{price}"

    def _getRewardArg(self):
        reward = MonetizationManager.getProductReward(self.prod_id, "Gold") or "?"
        return reward

    def _scopeInteract(self, source):
        SystemMonetization = SystemManager.getSystem("SystemMonetization")
        source.addScope(SystemMonetization.scopePay, self.prod_id)

    def _scopeInteractDummy(self, source):
        prod_params = self.prod_params
        source.addPrint("<GameStore> [{}] Dummy pay {} money for prod id {} ({!r}: {}) that returns {}".format(
            self.card_id, prod_params.price, self.prod_id, prod_params.name, prod_params.descr, prod_params.reward)
        )
