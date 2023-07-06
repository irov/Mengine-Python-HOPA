from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.MonetizationManager import MonetizationManager
from Foundation.PolicyManager import PolicyManager
from Foundation.SystemManager import SystemManager
from Foundation.TaskManager import TaskManager
from Foundation.Utils import SimpleLogger
from HOPA.Entities.SpecialPromotion.RewardPlate import RewardPlate
from HOPA.Entities.SpecialPromotion.PurchaseButton import PurchaseButton
from Event import Event


_Log = SimpleLogger("SpecialPromotion")

EVENT_WINDOW_CLOSE = Event("SpecialPromotionClosed")
EVENT_GET_PURCHASED = Event("SuccessPurchaseEvent")


class SpecialPromotion(BaseEntity):
    ALIAS_NEW_PRICE = "$SpecPromoNewPrice"
    ALIAS_OLD_PRICE = "$SpecPromoOldPrice"
    ALIAS_DISCOUNT = "$SpecPromoDiscount"
    ALIAS_TITLE = "$SpecPromoTitle"
    ALIAS_DESCRIPTION = "$SpecPromoDescr"
    ALIAS_REWARD_GOLD = "$SpecPromoGoldReward"
    ALIAS_REWARD_ENERGY = "$SpecPromoEnergyReward"

    def __init__(self):
        super(SpecialPromotion, self).__init__()
        self.content = {}
        self.backgrounds = {}
        self.icons = {}  # tag
        self.effects = {}
        self.params = {}  # tag
        self.current_tag = None
        self._observers = []

    def __loadParams(self):
        params = MonetizationManager.getSpecialPromotionParams()
        tagged = {param.tag: param for param in params.values()}
        return tagged

    def _onPreparation(self):
        self.params = self.__loadParams()

        aliases = [self.ALIAS_TITLE, self.ALIAS_DESCRIPTION, self.ALIAS_NEW_PRICE, self.ALIAS_OLD_PRICE]
        for alias in aliases:
            Mengine.setTextAlias("", alias, "ID_EMPTY")

        self._loadMovies()

    def _onActivate(self):
        self._observers.append(Notification.addObserver(Notificator.onProductsUpdateDone, self._onProductsUpdateDone))

    def _onDeactivate(self):
        self._cbCloseEnd()
        for icon in self.icons.values():
            icon.removeFromParent()
            icon.onDestroy()
        self.icons = {}
        for movie in self.content.values() + self.backgrounds.values():
            movie.returnToParent()
        self.content = {}
        self.backgrounds = {}

        for observer in self._observers:
            Notification.removeObserver(observer)
        self._observers = []

    def _onProductsUpdateDone(self):
        self._updateTexts()
        return False

    # /////////////

    def _getMovies(self, dict_in, dict_out, optional=False):
        for key, movie_name in dict_in.items():
            if self.object.hasObject(movie_name):
                movie = self.object.getObject(movie_name)
                movie.setInteractive(True)
                dict_out[key] = movie
                continue

            if optional is True:
                continue

            _Log("{}:{} not inited ({} hasn't this object)".format(key, movie_name, self.object.getName()), err=True)

    def _loadMovies(self):
        # init movies
        content = {
            "window": "Movie2_Window",
            "close": "Movie2Button_Close",
        }
        self._getMovies(content, self.content)

        optional_content = {
            "restore": "Movie2Button_Restore",
        }
        self._getMovies(optional_content, self.content, optional=True)

        backgrounds = {
            tag: param.background_movie_name for tag, param in self.params.items()
            if param.background_movie_name is not None
        }
        self._getMovies(backgrounds, self.backgrounds)

        effects = {
            "appear": "Movie2_Appear",
            "disappear": "Movie2_Disappear",
        }
        self._getMovies(effects, self.effects)

        # manage icons
        icon_slot = None
        if self.content["window"].hasSlot("icon") is False:
            Trace.log("Entity", 0, "SpecialPromotion: can't attach icons - add slot 'icon' to window")
        else:
            icon_slot = self.content["window"].getMovieSlot("icon")

        icons = {tag: "Movie2_Icon_" + tag for tag in self.params.keys()}
        for tag, proto in icons.items():
            if self.object.hasPrototype(proto):
                movie = self.object.generateObjectUnique(proto, proto, Enable=False)
                self.icons[tag] = movie

                if icon_slot is not None:
                    node = movie.getEntityNode()
                    icon_slot.addChild(node)
            else:
                _Log("{}:{} not created ({} hasn't this prototype)".format(tag, proto, self.object.getName()), err=True)

        # attach items
        self._attachContent("window", "close", "close")
        if "restore" in self.content:
            self._attachContent("window", "purchase", "restore")
        for background_movie in self.backgrounds.values():
            background_movie.setEnable(False)
            self._attachMovie("window", "bg", background_movie)

        # setup effect
        self.attachToEffect("appear")
        self.setEnableWindow(False)

        return True

    def _updateTexts(self):
        if self.current_tag is None:
            return

        params = self.params[self.current_tag]

        def with_currency(price):
            if price is None:
                return ""
            price_template = MonetizationManager.getGeneralSetting("StoreCardPriceTemplate", "{currency}{price}")
            currency = MonetizationManager.getCurrentCurrencySymbol() or ""
            text = price_template.format(currency=currency, price=price)
            return text

        texts = {  # alias: [text_id, *args]
            self.ALIAS_TITLE:
                [params.id_title],
            self.ALIAS_DESCRIPTION:
                [params.id_descr],
            self.ALIAS_NEW_PRICE:
                [params.id_new_price, with_currency(params.price)],
            self.ALIAS_OLD_PRICE:
                [params.id_old_price, with_currency(params.old_price)],
            self.ALIAS_DISCOUNT:
                [params.id_discount],
            self.ALIAS_REWARD_GOLD:
                [params.id_reward_gold, MonetizationManager.getProductReward(params.id, "Gold")],
            self.ALIAS_REWARD_ENERGY:
                [params.id_reward_energy, MonetizationManager.getProductReward(params.id, "Energy")]
        }
        self._setTexts(texts)

    def _setRewardsPlate(self, tag):
        params = self.params[tag]
        if params.reward_prototype_name is None:
            return False
        prototype_name = params.reward_prototype_name

        if self.object.hasPrototype(prototype_name) is False:
            return False

        movie = self.object.generateObjectUnique("RewardPlate", prototype_name)

        rewards = RewardPlate(movie)
        rewards.createIcons()
        rewards.setEnable(True)

        self.content["rewards"] = rewards
        self._attachContent("window", "rewards", "rewards")

        return True

    def _setPurchaseButton(self, tag):
        params = self.params[tag]

        if params.purchase_prototype_name is None:
            if self.object.hasObject("Movie2Button_Purchase"):
                self.content["purchase"] = self.object.getObject("Movie2Button_Purchase")
                self._attachContent("window", "purchase", "purchase")
                Trace.msg_err("SpecialPromotion [{!r}] DEPRECATED warning: Movie2Button_Purchase is deprecated, "
                              "add `PurchasePrototypeName` as prototype button".format(tag))
            else:
                Trace.log("Entity", 0, "SpecialPromotion [{!r}] not found "
                                       "purchase button - add `PurchasePrototypeName`".format(tag))
            return False

        prototype_name = params.reward_prototype_name
        if self.object.hasPrototype(prototype_name) is False:
            return False

        movie = self.object.generateObjectUnique("PurchaseButton", prototype_name)

        purchase = PurchaseButton(movie)
        purchase.setEnable(True)

        self.content["purchase"] = purchase
        self._attachContent("window", "purchase", "purchase")

        return True

    def setup(self, tag):
        if tag not in self.params:
            Trace.log("Entity", 0, "SpecialPromotion: wrong tag '{}'".format(tag))
            return False

        self.current_tag = tag

        icon = self.icons.get(tag)
        if icon is not None:
            icon.setEnable(True)
        else:
            Trace.msg_err("SpecialPromotion setup {}: icon not found".format(tag))

        self._updateTexts()
        self._setRewardsPlate(tag)
        if self._setPurchaseButton(tag) is False:
            return False

        return True

    # utils

    def _attachContent(self, parent_name, slot_name, child_name):
        if child_name not in self.content:
            Trace.log("Entity", 0, "_loadMovies - key '{}' not found".format(child_name))
            return False
        child = self.content[child_name]

        self._attachMovie(parent_name, slot_name, child)
        return True

    def _attachMovie(self, parent_name, slot_name, child):
        if self.content[parent_name].hasMovieSlot(slot_name) is False:
            Trace.log("Entity", 0, "_loadMovies - not found slot '{}' on '{}'".format(slot_name, parent_name))
            return False
        slot = self.content[parent_name].getMovieSlot(slot_name)

        child_node = child.getEntityNode()
        child_node.removeFromParent()
        slot.addChild(child_node)
        return True

    def _setTexts(self, texts_dict):
        """ :param texts_dict: { alias_id: [text_id, *args] }
                dict where key is alias and value is a list where first val is text_id and other is args """
        for alias, args in texts_dict.items():
            self._setText("", alias, *args)

    @staticmethod
    def _setText(env, alias, text_id, *args):
        if text_id is None:
            return

        Mengine.removeTextAliasArguments(env, alias)
        Mengine.setTextAlias(env, alias, text_id)

        text_args = [arg for arg in args if arg is not None]
        if len(text_args) > 0 and "%s" in Mengine.getTextFromId(text_id):
            Mengine.setTextAliasArguments(env, alias, *text_args)

    # --- effects ------------------------------------------------------------------------------------------------------

    def setEnableWindow(self, state):
        def _update(movie):
            movie.setEnable(state)
            movie.setLoop(state)
            movie.setPlay(state)

        _update(self.content["window"])
        if self.current_tag in self.backgrounds:
            _update(self.backgrounds[self.current_tag])
        if self.current_tag in self.icons:
            _update(self.icons[self.current_tag])

    def attachToEffect(self, effect):
        window_movie = self.content["window"]
        effect_movie = self.effects.get(effect, None)
        if effect_movie is None:
            Trace.log("Entity", 0, "attachToEffect: can't find effect '{}' in self.effects {}".format(effect, self.effects.keys()))
            return

        slot = effect_movie.getMovieSlot("window")
        if slot is None:
            Trace.log("Entity", 0, "attachToEffect: movie '{}' should has slot 'window'".format(effect_movie.getName()))
            return

        window_node = window_movie.getEntityNode()
        window_node.removeFromParent()
        slot.addChild(window_node)
        effect_movie.setLastFrame(False)  # set first frame

    def scopeOpen(self, source):
        appear_effect = self.effects.get("appear", None)
        disappear_effect = self.effects.get("disappear", None)

        source.addFunction(self.setEnableWindow, True)
        if None in [appear_effect, disappear_effect]:
            _Log("can't find effects for scope Open...", err=True)
        else:
            source.addEnable(appear_effect)
            source.addPlay(appear_effect, Wait=True)
            source.addDisable(appear_effect)
            source.addEnable(disappear_effect)
            source.addFunction(self.attachToEffect, "disappear")

    def _cbCloseEnd(self):
        self.setEnableWindow(False)
        if "rewards" in self.content:
            self.content.pop("rewards").cleanUp()
        if "purchase" in self.content:
            purchase = self.content.pop("purchase")
            if isinstance(self.content["Purchase"], PurchaseButton):
                purchase.cleanUp()
            else:
                purchase.returnToParent()
        self.current_tag = None
        EVENT_WINDOW_CLOSE()

    def scopeClose(self, source):
        appear_effect = self.effects.get("appear", None)
        disappear_effect = self.effects.get("disappear", None)

        if None in [appear_effect, disappear_effect]:
            _Log("can't find effects for scope Close...", err=True)
        else:
            source.addEnable(disappear_effect)
            source.addPlay(disappear_effect, Wait=True)
            source.addDisable(disappear_effect)
            source.addEnable(appear_effect)
            source.addFunction(self.attachToEffect, "appear")
        source.addFunction(self._cbCloseEnd)

    # --- interaction ---

    def run(self, special_prod_id):
        if TaskManager.existTaskChain("SpecialPromotion"):
            TaskManager.cancelTaskChain("SpecialPromotion")

        PolicyAuth = PolicyManager.getPolicy("Authorize", "PolicyDummy")
        TaskManager.runAlias(PolicyAuth, None)

        params = MonetizationManager.getSpecialPromoById(special_prod_id)
        if params is None:
            Trace.log("Entity", 0, "SpecialPromotion start failed - not found special promotion for product with id {}".format(special_prod_id))
            return False

        if MonetizationManager.hasProductInfo(params.id) is False:
            Trace.log("Entity", 0, "SpecialPromotion start failed [{}] - not found product with id {}".format(special_prod_id, params.id))
            return False

        if self.setup(params.tag) is False:
            return False

        with TaskManager.createTaskChain(Name="SpecialPromotion") as tc:
            with tc.addParallelTask(2) as (tc_show, tc_fade):
                tc_show.addScope(self.scopeOpen)
                tc_fade.addTask("AliasFadeIn", FadeGroupName="FadeUI", To=0.5, Time=250.0, ReturnItem=False)

            with tc.addRepeatTask() as (purchase, until):
                purchase.addScope(self._scopePurchaseClick)

                with until.addRaceTask(2) as (close, interrupt):
                    close.addTask("TaskMovie2ButtonClick", Movie2Button=self.content["close"])
                    interrupt.addEvent(EVENT_GET_PURCHASED)

            with tc.addParallelTask(2) as (tc_close, tc_fade):
                tc_close.addScope(self.scopeClose)
                tc_fade.addTask("AliasFadeOut", FadeGroupName="FadeUI", From=0.5, Time=250.0)

        return True

    def _scopePurchaseClick(self, source):
        def scopeSuccess(src):
            src.addFunction(EVENT_GET_PURCHASED)

        params = self.params[self.current_tag]
        SystemMonetization = SystemManager.getSystem("SystemMonetization")

        # if we got an alias product id - need real:
        product_id = MonetizationManager.getProductRealId(params.id)

        if product_id is None:
            source.addBlock()
            return

        if SystemMonetization.isPurchaseDelayed(product_id) is True:
            if "restore" in self.content:
                self.content["restore"].setEnable(True)
                self.content["purchase"].setEnable(False)

            source.addTask("TaskMovie2ButtonClick", Movie2Button=self.content.get("restore", "purchase"))
            with source.addParallelTask(2) as (purchased, release):
                purchased.addListener(Notificator.onPaySuccess, Filter=lambda prod_id: prod_id == product_id)
                purchased.addScope(scopeSuccess)
                release.addNotify(Notificator.onReleasePurchased, product_id)
        else:
            if "restore" in self.content:
                self.content["restore"].setEnable(False)
                self.content["purchase"].setEnable(True)

            source.addTask("TaskMovie2ButtonClick", Movie2Button=self.content["purchase"])
            source.addScope(SystemMonetization.scopePay, product_id, scopeSuccess=scopeSuccess)

