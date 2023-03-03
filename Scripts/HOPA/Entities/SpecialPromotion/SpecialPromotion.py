from Event import Event
from Foundation.DemonManager import DemonManager
from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.MonetizationManager import MonetizationManager
from Foundation.PolicyManager import PolicyManager
from Foundation.SystemManager import SystemManager
from Foundation.TaskManager import TaskManager
from Foundation.Utils import SimpleLogger, getCurrentPublisher


_Log = SimpleLogger("SpecialPromotion")

EVENT_WINDOW_CLOSE = Event("SpecialPromotionClosed")
EVENT_GET_PURCHASED = Event("SuccessPurchaseEvent")


class SpecialPromotion(BaseEntity):
    ALIAS_NEW_PRICE = "$SpecPromoNewPrice"
    ALIAS_OLD_PRICE = "$SpecPromoOldPrice"
    ALIAS_TITLE = "$SpecPromoTitle"
    ALIAS_DESCRIPTION = "$SpecPromoDescr"
    ALIAS_REWARD_GOLD = "$SpecPromoGoldReward"
    ALIAS_REWARD_ENERGY = "$SpecPromoEnergyReward"

    def __init__(self):
        super(SpecialPromotion, self).__init__()
        self.content = {}
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

        self.__loadMovies()

    def _onActivate(self):
        self._observers.append(Notification.addObserver(Notificator.onProductsUpdateDone, self._onProductsUpdateDone))

    def _onDeactivate(self):
        self._cbCloseEnd()
        for icon in self.icons.values():
            icon.removeFromParent()
            icon.onDestroy()
        self.icons = {}
        for movie in self.content.values():
            movie.returnToParent()

        for observer in self._observers:
            Notification.removeObserver(observer)
        self._observers = []

    def _onProductsUpdateDone(self):
        self._updateTexts()
        return False

    # /////////////

    def __loadMovies(self):
        def _getMovies(dict_in, dict_out):
            for key, movie_name in dict_in.items():
                if self.object.hasObject(movie_name):
                    movie = self.object.getObject(movie_name)
                    movie.setInteractive(True)
                    dict_out[key] = movie
                else:
                    _Log("{}:{} not inited ({} hasn't this object)".format(key, movie_name, self.object.getName()), err=True)

        content = {
            "window": "Movie2_Window",
            "purchase": "Movie2Button_Purchase",
            "close": "Movie2Button_Close",
        }
        _getMovies(content, self.content)

        effects = {
            "appear": "Movie2_Appear",
            "disappear": "Movie2_Disappear",
        }
        _getMovies(effects, self.effects)

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

        self._attach("window", "close", "close")
        self._attach("window", "purchase", "purchase")

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
            self.ALIAS_TITLE: [params.id_title],
            self.ALIAS_DESCRIPTION: [params.id_descr],
            self.ALIAS_NEW_PRICE: [params.id_new_price, with_currency(params.price)],
            self.ALIAS_OLD_PRICE: [params.id_old_price, with_currency(params.old_price)]
        }
        self.__setTexts(texts)

    def _setRewardsPlate(self, tag):
        if self.object.hasPrototype("Movie2_Rewards") is False:
            return

        params = self.params[tag]

        if params.use_reward_plate is False:
            return

        texts = {
            self.ALIAS_REWARD_GOLD:
                [params.id_reward_gold, MonetizationManager.getProductReward(params.id, "Gold")],
            self.ALIAS_REWARD_ENERGY:
                [params.id_reward_energy, MonetizationManager.getProductReward(params.id, "Energy")]
        }
        self.__setTexts(texts)

        movie = self.object.generateObjectUnique("Movie2_Rewards", "Movie2_Rewards")

        rewards = RewardPlate(movie)
        rewards.createIcons()
        rewards.setEnable(True)

        self.content["rewards"] = rewards
        self._attach("window", "rewards", "rewards")

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

        return True

    # utils

    def _attach(self, parent_name, slot_name, child_name):
        if self.content[parent_name].hasMovieSlot(slot_name) is False:
            Trace.log("Entity", 0, "__loadMovies - not found slot '{}' on '{}'".format(slot_name, parent_name))
            return False
        slot = self.content[parent_name].getMovieSlot(slot_name)

        if child_name not in self.content:
            Trace.log("Entity", 0, "__loadMovies - key '{}' not found".format(child_name))
            return False
        child = self.content.get(child_name)

        child_node = child.getEntityNode()
        child_node.removeFromParent()
        slot.addChild(child_node)
        return True

    def __setTexts(self, texts_dict):
        """ :param texts_dict: { alias_id: [text_id, *args] }
                dict where key is alias and value is a list where first val is text_id and other is args """
        for alias, args in texts_dict.items():
            self.__setText("", alias, *args)

    def __setText(self, env, alias, text_id, *args):
        Mengine.removeTextAliasArguments(env, alias)
        Mengine.setTextAlias(env, alias, text_id)
        text_args = [arg for arg in args if arg is not None]
        if len(text_args) > 0 and "%s" in Mengine.getTextFromID(text_id):
            Mengine.setTextAliasArguments(env, alias, *text_args)

    # --- effects ------------------------------------------------------------------------------------------------------

    def setEnableWindow(self, state):
        self.content["window"].setEnable(state)
        self.content["window"].setLoop(state)
        self.content["window"].setPlay(state)
        icon = self.icons.get(self.current_tag)
        if icon is not None:
            icon.setEnable(state)

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

        if self.setup(params.tag) is False:
            return False

        SystemMonetization = SystemManager.getSystem("SystemMonetization")
        # if we got an alias product id - need real:
        product_id = MonetizationManager.getProductInfo(special_prod_id).id

        def scopeSuccess(source):
            source.addFunction(EVENT_GET_PURCHASED)

        with TaskManager.createTaskChain(Name="SpecialPromotion") as tc:
            with tc.addParallelTask(2) as (tc_show, tc_fade):
                tc_show.addScope(self.scopeOpen)
                tc_fade.addTask("AliasFadeIn", FadeGroupName="FadeUI", To=0.5, Time=250.0)

            with tc.addRepeatTask() as (purchase, until):
                purchase.addTask("TaskMovie2ButtonClick", Movie2Button=self.content["purchase"])
                purchase.addScope(SystemMonetization.scopePay, product_id, scopeSuccess=scopeSuccess)

                with until.addRaceTask(2) as (close, interrupt):
                    close.addTask("TaskMovie2ButtonClick", Movie2Button=self.content["close"])
                    interrupt.addEvent(EVENT_GET_PURCHASED)

            with tc.addParallelTask(2) as (tc_close, tc_fade):
                tc_close.addScope(self.scopeClose)
                tc_fade.addTask("AliasFadeOut", FadeGroupName="FadeUI", From=0.5, Time=250.0)

        return True


class RewardPlate(object):

    def __init__(self, movie):
        self.movie = movie
        self.icons = []

    def createIcons(self):
        game_store_name = MonetizationManager.getGeneralSetting("GameStoreName", "GameStore")
        current_publisher = getCurrentPublisher()
        GameStore = DemonManager.getDemon(game_store_name)

        def _createIcon(slot_name, object_name):
            slot = self.movie.getMovieSlot(slot_name)
            icon = GameStore.generateIcon(object_name, "{}_{}".format(object_name, current_publisher), Enable=True)
            slot.addChild(icon.getEntityNode())
            self.icons.append(icon)

        _createIcon("gold", "Movie2_Coin")
        _createIcon("energy", "Movie2_Energy")

    def getEntityNode(self):
        return self.movie.getEntityNode()

    def setEnable(self, state):
        self.movie.setEnable(bool(state))

    def cleanUp(self):
        to_destroy = self.icons + [self.movie]

        for movie in to_destroy:
            movie.removeFromParent()
            movie.onDestroy()

        self.icons = None
        self.movie = None
