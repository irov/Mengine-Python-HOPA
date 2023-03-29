from Foundation.DemonManager import DemonManager
from Foundation.GroupManager import GroupManager
from Foundation.MonetizationManager import MonetizationManager
from Foundation.SystemManager import SystemManager
from Foundation.Providers.PaymentProvider import PaymentProvider
from HOPA.StoreManager import StoreManager


class ButtonMixin(object):
    aliases = {}
    _submovies = []
    action = None

    if _DEVELOPMENT is True:
        def __repr__(self):
            return "<{} [{}:{}]>".format(self.__class__.__name__, self.params.page_id, self.id)

    def __init__(self, params, button_movie, icon_movie):
        self.id = params.button_id
        self.params = params
        self.product_params = MonetizationManager.getProductInfo(params.product_id)

        self.movie = button_movie
        self.icon_movie = icon_movie
        if icon_movie is not None:
            self.attach("icon", icon_movie)
        self.notify_movie = None

        self.env = str(self.id)
        self._initText()

        self._prepare()

    # Working with text

    def _getTextID(self, alias_id):
        alias_and_text_ids = self._getAliasAndTextID()
        alias = self.aliases[alias_id]
        text_id = alias_and_text_ids[alias]
        return text_id

    def _getAliasAndTextID(self):
        return {}

    def _initText(self):
        self.movie.setTextAliasEnvironment(self.env)

        alias_and_text_ids = self._getAliasAndTextID()
        for alias, text_id in alias_and_text_ids.items():
            Mengine.setTextAlias(self.env, alias, text_id)

        self.setText()

    def setText(self):
        """ method that setups text arguments to the aliases """

    def setTextArguments(self, alias_id, *args):
        """ alias_id is from param aliases"""
        if alias_id not in self.aliases:
            Trace.log("Entity", 0, "Not found alias_id={!r} in aliases dict. Available: {}".format(alias_id, self.aliases.keys()))
            return
        alias = self.aliases[alias_id]
        Mengine.setTextAliasArguments(self.env, alias, *args)

    # Working with attachments and states

    def _prepare(self):
        pass

    def hasNotify(self):
        return False

    def attach(self, slot_name, movie):
        node = movie.getEntityNode()
        self.movie.addChildToSlot(node, slot_name)

    def detach(self, slot_name, movie):
        node = movie.getEntityNode()
        self.movie.removeFromParentSlot(node, slot_name)

    def attachNotify(self, movie):
        if self.notify_movie is not None:
            self.removeNotify()

        self.attach("notify", movie)
        self.notify_movie = movie

    def removeNotify(self):
        if self.notify_movie is None:
            return

        self.detach("notify", self.notify_movie)
        self.notify_movie.onDestroy()
        self.notify_movie = None

    def setEnable(self, state):
        self.movie.setEnable(state)
        if self.icon_movie is not None:
            self.icon_movie.setEnable(state)

    def setBlock(self, state):
        self.movie.setBlock(state)

    def hasSubmovie(self, submovie_name):
        for movie in self.movie.eachMovies():
            if movie.entity.hasSubMovie(submovie_name) is True:
                return True
        return False

    def setEnableSubmovie(self, submovie_name, state):
        if self.hasSubmovie(submovie_name) is False:
            Trace.log("Entity", 1, "Store Button {} has no submovie {}".format(self.id, submovie_name))
            return

        for movie in self.movie.eachMovies():
            disable_layers = movie.getParam("DisableSubMovies")
            if state is True and submovie_name in disable_layers:
                movie.delParam("DisableSubMovies", submovie_name)
            elif state is False and submovie_name not in disable_layers:
                movie.appendParam("DisableSubMovies", submovie_name)

    def setPlay(self, state, Loop=True):
        for movie in self.movie.eachMovies():
            movie.setLoop(Loop)
            movie.setPlay(state)

            # todo: play, loop for each submovie (from _submovies)
            #       animatable.play, loop is not working because of "not initialized error"

    # CleanUp

    def cleanUp(self):
        if self.icon_movie is not None:
            self.icon_movie.removeFromParent()
            self.icon_movie.onDestroy()
            self.icon_movie = None

        self.removeNotify()

        if self.movie is not None:
            self.movie.removeFromParent()
            self.movie.onDestroy()
            self.movie = None

        self.params = None

    # Scopes

    def scopeClick(self, source):
        source.addTask("TaskMovie2ButtonClick", isDown=False, Movie2Button=self.movie)

    def scopeAction(self, source):
        source.addBlock()


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
        if "%s" in Mengine.getTextFromID(price_text_id):
            currency = MonetizationManager.getCurrentCurrencySymbol() or ""
            self.setTextArguments("price", self.price_template.format(currency=currency, price=product.price))

        reward = product.reward
        self.setTextArguments("gold", reward.get("Gold", 0))
        self.setTextArguments("energy", reward.get("Energy", 0))

        discount_text_id = self._getTextID("discount")
        discount_text = Mengine.getTextFromID(discount_text_id)
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
        product_id = self.params.product_id
        source.addFunction(PaymentProvider.pay, product_id)


class ButtonAdvert(ButtonMixin):
    aliases = {
        "title": "$AliasStoreButtonTitle",
        "descr": "$AliasStoreButtonDescr",
        "gold": "$AliasStoreGoldReward",
        "energy": "$AliasStoreEnergyReward",
        "reset_timer": "$AliasStoreAdvertTimer",
        "ads_counter": "$AliasStoreAdvertCounter"
    }
    action = "advert"

    # Texts

    def _getAliasAndTextID(self):
        alias_param = {
            self.aliases["title"]: self.params.title_text_id,
            self.aliases["descr"]: self.params.descr_text_id,
            self.aliases["gold"]: self.params.gold_reward_text_id,
            self.aliases["energy"]: self.params.energy_reward_text_id,
            self.aliases["reset_timer"]: self.params.timer_text_id,
            self.aliases["ads_counter"]: self.params.counter_text_id,
        }
        return alias_param

    def setText(self):
        reward = self.product_params.reward
        if reward is not None:
            self.setTextArguments("gold", reward.get("Gold", 0))
            self.setTextArguments("energy", reward.get("Energy", 0))
        self.setTextArguments("reset_timer", "")
        self.setTextArguments("ads_counter", 0, 0)

    # States

    def hasNotify(self):
        if SystemManager.hasSystem("SystemMonetization") is True:
            SystemMonetization = SystemManager.getSystem("SystemMonetization")
            if SystemMonetization.isAdsEnded() is False:
                return True
        return False

    def updateTimer(self, *args):
        self.setTextArguments("reset_timer", *args)

    def updateCounter(self, current, maximum):
        self.setTextArguments("ads_counter", current, maximum)

    # Scopes

    def scopeAction(self, source):
        source.addTask("AliasShowAdvert", AdType="Rewarded")


# FACTORY


class ButtonFactory(object):
    allowed_actions = {"purchase": ButtonPurchase, "advert": ButtonAdvert}
    objects = []  # [ ConcreteButton, ... ]
    page_objects = {}  # { page_id: { button_id: ConcreteButton, ... }, ... }

    @classmethod
    def _updateButtonsParams(cls):
        if MonetizationManager.getGeneralSetting("StoreCardPriceCurrencyPosition", "left") == "left":
            price_template = "{currency}{price}"
        else:  # position is 'right'
            price_template = "{price}{currency}"
        price_template = MonetizationManager.getGeneralSetting("StoreCardPriceTemplate", price_template)
        ButtonPurchase.price_template = price_template

    @classmethod
    def createPageButtons(cls, page_id):
        cls._updateButtonsParams()

        buttons = []

        button_params = StoreManager.getButtonsParamsById(page_id)
        for param in button_params.values():
            group_name = param.prototype_group

            if group_name.startswith("Demon_"):
                group = DemonManager.getDemon(group_name)
            else:
                group = GroupManager.getGroup(group_name)

            button_movie = group.tryGenerateObjectUnique(param.button_prototype, param.button_prototype)
            icon_movie = None
            if param.icon_prototype is not None:
                icon_movie = group.tryGenerateObjectUnique(param.icon_prototype, param.icon_prototype)

            button = ButtonFactory.createButton(param, button_movie, icon_movie)
            if button is None:
                continue
            buttons.append(button)

        return buttons

    @classmethod
    def createButton(cls, params, button_movie, icon_movie):
        page_id = params.page_id

        if params.action not in cls.allowed_actions:
            Trace.log("Manager", 0, "ButtonFactory [{!r}] not found action {!r}".format(params.button_id, params.action))
            button = ButtonMixin(params, button_movie, icon_movie)
            button.cleanUp()
            return None

        ConcreteButton = cls.allowed_actions[params.action]
        button = ConcreteButton(params, button_movie, icon_movie)
        button.setPlay(True, Loop=True)

        if page_id not in cls.page_objects:
            cls.page_objects[page_id] = {}
        cls.page_objects[page_id][params.button_id] = button
        cls.objects.append(button)

        # print " * [{}] created button {} [{}] from {} for slot:{} ".format(params.page_id, params.action, params.button_id, params.prototype, params.slot_name)

        return button

    @classmethod
    def cleanPageObjects(cls, page_id):
        if len(cls.page_objects) == 0:
            return True

        if page_id not in cls.page_objects:
            Trace.log("Manager", 0, "ButtonFactory page_id {!r} not found".format(page_id))
            return False

        for button_id, button in cls.page_objects.pop(page_id).items():
            button.cleanUp()
            cls.objects.remove(button)
        return True

    @classmethod
    def cleanObjects(cls):
        # print "!!!!!!!! CLEAN OBJECTS !!!!!!!!!!"
        for button in cls.objects:
            button.cleanUp()
        cls.objects = []
        cls.page_objects = {}

    @classmethod
    def getAllButtons(cls):
        """ returns list of all created buttons """
        return cls.objects

    @classmethod
    def getPageButtons(cls, page_id):
        """ returns dict like { page_id: { button_id: ConcreteButton, ... }, ... } """
        return cls.page_objects.get(page_id, {})
