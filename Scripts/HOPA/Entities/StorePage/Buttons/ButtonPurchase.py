from Foundation.MonetizationManager import MonetizationManager
from Foundation.Providers.PaymentProvider import PaymentProvider
from HOPA.Entities.StorePage.Buttons.ButtonMixin import ButtonMixin


class ButtonPurchase(ButtonMixin):
    aliases = {
        "price": "$AliasStoreButtonPrice",
        "title": "$AliasStoreButtonTitle",
        "descr": "$AliasStoreButtonDescr",
        "energy": "$AliasStoreEnergyReward",
        "gold": "$AliasStoreGoldReward",
        "discount": "$AliasStoreButtonDiscount",
    }
    action = "purchase"
    price_template = "{currency}{value}"

    # Texts

    def _getAliasAndTextID(self):
        alias_param = {
            self.aliases["price"]: self.params.price_text_id,
            self.aliases["title"]: self.params.title_text_id,
            self.aliases["descr"]: self.params.descr_text_id,
            self.aliases["gold"]: self.params.gold_reward_text_id,
            self.aliases["energy"]: self.params.energy_reward_text_id,
            self.aliases["discount"]: self.params.discount_text_id,
        }
        return alias_param

    def setText(self):
        # StoreManager guarantees that product exists
        product = self.product_params

        price_text_id = self._getTextID("price")
        if "%s" in Mengine.getTextFromId(price_text_id):
            currency = MonetizationManager.getCurrentCurrencySymbol() or ""
            self.setTextArguments("price", self.price_template.format(currency=currency, price=product.price))

        reward = product.reward
        self.setTextArguments("gold", reward.get("Gold", 0))
        self.setTextArguments("energy", reward.get("Energy", 0))

        discount_text_id = self._getTextID("discount")
        discount_text = Mengine.getTextFromId(discount_text_id)
        if "%s" in discount_text:
            if "%%" in discount_text:
                # if our text has '%' - we want to add discount percent
                self.setTextArguments("discount", product.discount)
            else:
                # otherwise it would be discounted price (price/discount)
                self.setTextArguments("discount", product.discount_price)

    def _prepare(self):
        self._submovies = ["BonusTag", self.params.discount_submovie]

        if self.hasSubmovie(self.params.discount_submovie) is True:
            if self.product_params.discount is not None:
                self.setEnableSubmovie(self.params.discount_submovie, True)
            else:
                self.setEnableSubmovie(self.params.discount_submovie, False)

    # Scopes

    def scopeAction(self, source):
        product_id = MonetizationManager.getProductRealId(self.params.product_id)
        source.addFunction(PaymentProvider.pay, product_id)
