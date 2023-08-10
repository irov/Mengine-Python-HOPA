from Foundation.DemonManager import DemonManager
from Foundation.GroupManager import GroupManager
from Foundation.MonetizationManager import MonetizationManager
from HOPA.Entities.StorePage.Buttons.ButtonMixin import ButtonMixin


class ButtonExchange(ButtonMixin):
    aliases = {
        "price": "$AliasStoreButtonPrice",
        "title": "$AliasStoreButtonTitle",
        "descr": "$AliasStoreButtonDescr",
        "energy": "$AliasStoreEnergyReward",
        "gold": "$AliasStoreGoldReward",
        "discount": "$AliasStoreButtonDiscount",
    }
    action = "exchange"

    def __init__(self, params, button_movie, icon_movie):
        self.currency_icon_movie = None
        super(ButtonExchange, self).__init__(params, button_movie, icon_movie)

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
        reward = self.product_params.reward
        if reward is not None:
            self.setTextArguments("gold", reward.get("Gold", 0))
            self.setTextArguments("energy", reward.get("Energy", 0))

        self.setTextArguments("price", self.product_params.price)

    # Prepare

    def _getIconProvider(self):
        provider = MonetizationManager.getGeneralSetting("GameStoreName", "GameStore")
        if DemonManager.hasDemon(provider):
            return DemonManager.getDemon(provider)
        elif GroupManager.hasGroup(provider):
            return GroupManager.getGroup(provider)
        return None

    def _generateCurrencyIcon(self, currency):
        if currency == "Gold":
            icon_tag = "Coin"
        elif currency == "Energy":
            icon_tag = "Energy"
        else:
            Trace.log("Entity", 0, "{} [{}] has unknown currency {}".format(self.__class__.__name__, self.id, currency))
            return None

        icon_provider_object = self._getIconProvider()
        if icon_provider_object is None:
            Trace.log("Entity", 0, "{} [{}] not found icon provider".format(self.__class__.__name__, self.id))
            return None

        icon_name = "Movie2_{}_{}".format(icon_tag, Utils.getCurrentPublisher())
        object_name = "Movie2_Icon_{}".format(currency)
        try:
            icon_movie = icon_provider_object.generateIcon(object_name, icon_name)
        except AttributeError:
            icon_movie = icon_provider_object.generateObjectUnique(object_name, icon_name)

        if icon_movie is None:
            Trace.log("Entity", 0, "{} [{}] icon not created: object_name={}, icon_name={}".format(self.__class__.__name__, self.id, object_name, icon_name))

        return icon_movie

    def _prepare(self):
        currency = self.product_params.getCurrency()
        currency_icon_movie = self._generateCurrencyIcon(currency)
        if currency_icon_movie is None:
            return
        self.attach("currency", currency_icon_movie)
        currency_icon_movie.setEnable(True)
        self.currency_icon_movie = currency_icon_movie

    def cleanUp(self):
        if self.currency_icon_movie is not None:
            self.detach("currency", self.currency_icon_movie)
            self.currency_icon_movie.onDestroy()
            self.currency_icon_movie = None

        super(ButtonExchange, self).cleanUp()

    # Scopes

    def _scopeAction(self, source):
        currency = self.product_params.getCurrency()
        price = self.product_params.price

        # todo: move to Task

        currency_page_id = MonetizationManager.getGeneralSetting("%sPageID" % currency)
        if currency_page_id is None:
            currency_page_id = MonetizationManager.getGeneralSetting("NotEnoughMoneyPageID")

        if currency == "Gold":
            with source.addParallelTask(2) as (response, request):
                with response.addRaceTask(3) as (success, fail, not_enough_money):
                    success.addListener(Notificator.onGameStorePayGoldSuccess, Filter=lambda gold, *_: gold == price)
                    success.addNotify(Notificator.onPaySuccess, self.product_params.id)  # send reward

                    fail.addListener(Notificator.onGameStorePayGoldFailed)  # do nothing
                    fail.addDelay(0)

                    not_enough_money.addListener(Notificator.onGameStoreNotEnoughGold)
                    not_enough_money.addNotify(Notificator.onStoreSetPage, currency_page_id)   # open gold shop

                request.addNotify(Notificator.onGameStorePayGold, price, "Exchange")
        elif currency == "Energy":
            source.addPrint("not realized...")  # todo
        else:
            source.addPrint("!!! not found currency {}".format(currency))
