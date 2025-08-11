from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.MonetizationManager import MonetizationManager
from Foundation.PolicyManager import PolicyManager
from Foundation.SystemManager import SystemManager
from Foundation.TaskManager import TaskManager
from Foundation.Utils import SimpleLogger
from Foundation.Utils import getCurrentPublisher

from HOPA.Entities.GameStore.StoreCards.StoreCardAdvert import StoreCardAdvert
from HOPA.Entities.GameStore.StoreCards.StoreCardDefault import StoreCardDefault

ALIAS_COINS = "$AliasGameStoreCoinsCount"
ALIAS_ENV = ""
TEXT_ID_COINS = "ID_TEXT_GAMESTORE_BALANCE"
TEXT_ID_EMPTY = "ID_EMPTY"

_Log = SimpleLogger("GameStore")

class GameStore(BaseEntity):
    @staticmethod
    def declareORM(Type):
        BaseEntity.declareORM(Type)
        Type.addAction(Type, "UnblockAdTimestamp")

    def __init__(self):
        super(GameStore, self).__init__()
        self.__tcs = []
        self.red_dot_state = True

        self.observers = []

        self.content = {}
        self.cards = {}
        self.effects = {}
        self.cards_count = 0

    def _onPreparation(self):
        self.__initTexts()

        self.__loadMovies()
        if self.isStoreEnable() is True:
            self.__initMovies()
        else:  # I think would be better if we disable group instead of its children, but not today...
            for movie in self.content.values() + self.effects.values():
                movie.setEnable(False)

    def _onActivate(self):
        if self.isStoreEnable() is False:
            return

        observers = [
            Notification.addObserver(Notificator.onUpdateGoldBalance, self.refreshBalance),
            Notification.addObserver(Notificator.onAvailableAdsEnded, self.__onAdsEnded),
            Notification.addObserver(Notificator.onProductsUpdateDone, self._onProductsUpdateDone)
        ]
        self.observers = observers

        ad_card = self.getAdCard()
        if ad_card is not None:
            self.ad_time_block_observer = ad_card.TIME_BLOCK_EVENT.addObserver(self._cbAdTimeBlock)

        self.__runTaskChains()

    def _onDeactivate(self):
        for tc in self.__tcs:
            tc.cancel()
        self.__tcs = []

        for card in self.cards.values():
            if isinstance(card, StoreCardAdvert):
                self.object.setParam("UnblockAdTimestamp", card.unblock_timestamp)
            card.cleanUp()
        self.cards = {}

        for observer in self.observers:
            Notification.removeObserver(observer)
        self.observers = []
        self.ad_time_block_observer = None  # observer removes automatically in card cleanup

        if "balance_coin" in self.content:
            coin = self.content.pop("balance_coin")
            balance = self.content["balance"]
            balance.removeFromParentSlot(coin.getEntityNode(), "coin")
            coin.onDestroy()

        self.content = {}

    # --- Preparation --------------------------------------------------------------------------------------------------

    @staticmethod
    def isStoreEnable():
        b_monetization = MonetizationManager.isMonetizationEnable()
        b_enable = MonetizationManager.getGeneralSetting("EnableGameStore", False)
        return all([b_monetization, b_enable])

    def __initTexts(self):
        if self.isStoreEnable() is False:
            Mengine.setTextAlias(ALIAS_ENV, ALIAS_COINS, TEXT_ID_EMPTY)
            return

        Mengine.setTextAlias(ALIAS_ENV, ALIAS_COINS, TEXT_ID_COINS)

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
            "close": "Movie2Button_CloseWindow",
            "balance": "Movie2Button_Balance",
            "indicator": "Movie2_Indicator"
        }
        _getMovies(content, self.content)

        effects = {
            "appear": "Movie2_Appear",
            "disappear": "Movie2_Disappear",
        }
        _getMovies(effects, self.effects)

    def __initMovies(self):
        # step 1. Init window, effects, balance, indicator
        # self.__loadMovies() <---- in preparation

        # step 2. Create store cards
        if self.createStoreCards() is False:
            return False

        # step 3. Attach button close to window
        close_slot = self.content["window"].getMovieSlot("close")
        if close_slot is None:
            Trace.log("Entity", 0, "GameStore::__initMovies - can't attach button close to window, add slot 'close'")
            return False
        close_node = self.content["close"].getEntityNode()
        close_node.removeFromParent()
        close_slot.addChild(close_node)

        # step 4. Attach window to start effect
        self.attachToEffect("appear")
        self.setEnableStore(False)

        # step 5. Setup balance and advert indicator
        balance_movie = self.content["balance"]
        balance_movie.setEnable(True)
        indicator_movie = self.content.get("indicator")
        if indicator_movie is not None:
            indicator_node = indicator_movie.getEntityNode()
            balance_movie.addChildToSlot(indicator_node, "indicator")

            enable_ad_indicator = MonetizationManager.getGeneralSetting("UseAdvertIndicator")
            indicator_movie.setEnable(enable_ad_indicator)
            self.refreshAdIndicator()

        # (step 5) add coin reference
        coin_prototype = "Movie2_Coin_%s" % getCurrentPublisher()
        if self.object.hasPrototype(coin_prototype) is True:
            coin = self.object.generateObjectUnique("Movie2_Coin", coin_prototype)
            coin.setTextAliasEnvironment("balance")
            Mengine.setTextAlias("balance", "$AliasCoinUsePrice", "ID_EMPTY")
            balance_movie.addChildToSlot(coin.getEntityNode(), "coin")
            coin.setEnable(True)
            self.content["balance_coin"] = coin

        self.refreshBalance()

        return True

    def createStoreCards(self):
        if len(self.cards) > 0:
            Trace.log("Entity", 0, "StoreCards are already created!")
            return False

        StoreCardAdvert.unblock_timestamp = self.object.getParam("UnblockAdTimestamp")

        if MonetizationManager.getGeneralSetting("StoreCardPriceCurrencyPosition", "left") == "left":
            PRICE_TEMPLATE = "{currency}{price}"
        else:  # position is 'right'
            PRICE_TEMPLATE = "{price}{currency}"
        StoreCardDefault.PRICE_TEMPLATE = PRICE_TEMPLATE

        self.cards_count = MonetizationManager.getGeneralSetting("StoreItemsCount")
        for i in range(1, self.cards_count + 1):
            card_id = str(i)
            if self._createStoreCard(card_id) is False:
                return False
        return True

    def _createStoreCard(self, num):
        # -- get settings
        image_params = MonetizationManager.getImageParamsById(num)
        card_params = MonetizationManager.getCardParamsById(num)

        # -- create objects
        card = self.object.generateObjectUnique("StoreCard_%s" % num, card_params.prototype, Enable=True)
        image = self.object.generateObjectUnique("StoreImage_%s" % num, image_params.prototype, Enable=True)

        if num == str(MonetizationManager.getGeneralSetting("AdvertItemID")):
            store_card = StoreCardAdvert()
        else:
            store_card = StoreCardDefault()
        store_card.init(num, card, image, card_params)

        # -- attach card to window
        card_slot_name = "item%s" % num
        card_slot = self.content["window"].getMovieSlot(card_slot_name)
        if card_slot is None:
            Trace.log("GameStore::_createStoreCard #{} - can't find slot {!r} for attach card on window".format(num, card_slot_name))
            store_card.cleanUp()
            return False

        card_node = card.getEntityNode()
        card_slot.addChild(card_node)

        self.cards[num] = store_card

        return True

    def refreshCardsTexts(self):
        for card in self.cards.values():
            card.setTexts()

    # --- Store Interaction --------------------------------------------------------------------------------------------

    def __runTaskChains(self):
        tc_purchase = TaskManager.createTaskChain(Repeat=True)
        tc_handle_ui = TaskManager.createTaskChain(Repeat=True)
        self.__tcs.append(tc_purchase)
        self.__tcs.append(tc_handle_ui)

        with tc_handle_ui as tc:
            with tc.addRaceTask(2) as (tc_open, tc_close):
                tc_open.addTask('TaskMovie2ButtonClick', Movie2Button=self.content["balance"], isDown=True)
                tc_open.addScope(self.scopeOpenStore)

                tc_close.addTask('TaskMovie2ButtonClick', Movie2Button=self.content["close"], isDown=True)
                tc_close.addScope(self.scopeCloseStore)

        with tc_purchase as tc:
            for card, tc_purchase in tc.addRaceTaskList(self.cards.values()):
                tc_purchase.addTask("TaskMovie2ButtonClick", Movie2Button=card.movie_card)
                tc_purchase.addScope(card.scopeInteract)

    def refreshBalance(self, gold=None):
        Mengine.setTextAliasArguments(ALIAS_ENV, ALIAS_COINS, str(gold))
        return False

    def _onProductsUpdateDone(self):
        self.refreshCardsTexts()
        return False

    # --- Advertisement ------------------------------------------------------------------------------------------------

    def __onAdsEnded(self, ad_name=None):    # todo: add support for multi ad units
        ad_card = self.getAdCard()
        if ad_card is None:
            return True

        self.setRedDotState(False)
        if ad_card.unblock_timestamp is None:
            ad_card.setBlock(True)
        return False

    def getAdCard(self):
        for card in self.cards.values():
            if isinstance(card, StoreCardAdvert):
                return card

    @staticmethod
    def isAdsEnded():
        if SystemManager.hasSystem("SystemMonetization") is False:
            return False

        SystemMonetization = SystemManager.getSystem("SystemMonetization")
        return SystemMonetization.isAdsEnded() is True

    def refreshAdIndicator(self):
        if self.isAdsEnded() is True:
            self.__onAdsEnded()
            return

        if self.object.getParam("UnblockAdTimestamp") is not None:
            self.setRedDotState(False)

    def setRedDotState(self, state):
        self.red_dot_state = state
        indicator = self.content["indicator"]
        indicator.setEnable(state)

    def _cbAdTimeBlock(self, state):
        self.setRedDotState(not state)
        return False

    # --- Open/Close methods -------------------------------------------------------------------------------------------

    def setEnableStore(self, state):
        self.content["window"].setEnable(state)
        self.content["close"].setEnable(state)
        for card in self.cards.values():
            card.setEnable(state)

    def attachToEffect(self, effect):
        window_movie = self.content["window"]
        effect_movie = self.effects.get(effect, None)
        if effect_movie is None:
            Trace.log("Entity", 0, "GameStore.attachToEffect: can't find effect '{}' in self.effects {}".format(effect, self.effects.keys()))
            return

        slot = effect_movie.getMovieSlot("window")
        if slot is None:
            Trace.log("Entity", 0, "GameStore.attachToEffect: movie '{}' should has slot 'window'".format(effect_movie.getName()))
            return

        window_node = window_movie.getEntityNode()
        window_node.removeFromParent()
        slot.addChild(window_node)
        effect_movie.setLastFrame(False)  # set first frame

    def scopeOpenStore(self, source):
        PolicyAuth = PolicyManager.getPolicy("Authorize", "PolicyDummy")
        TaskManager.runAlias(PolicyAuth, None)

        with source.addParallelTask(2) as (source_open, source_fade):
            source_open.addScope(self._scopeOpenStore)
            source_fade.addTask("AliasFadeIn", FadeGroupName="FadeUI", To=0.5, Time=250.0, ReturnItem=False)

    def _scopeOpenStore(self, source):
        appear_effect = self.effects.get("appear", None)
        disappear_effect = self.effects.get("disappear", None)

        source.addFunction(self.setEnableStore, True)
        if None in [appear_effect, disappear_effect]:
            Trace.msg("<GameStore> can't find effects for scope OpenStore...")
        else:
            source.addEnable(appear_effect)
            source.addPlay(appear_effect, Wait=True)
            source.addDisable(appear_effect)
            source.addEnable(disappear_effect)
            source.addFunction(self.attachToEffect, "disappear")

    def scopeCloseStore(self, source):
        with source.addParallelTask(2) as (source_close, source_fade):
            source_close.addScope(self._scopeCloseStore)
            source_fade.addTask("AliasFadeOut", FadeGroupName="FadeUI", From=0.5, Time=250.0)

    def _scopeCloseStore(self, source):
        appear_effect = self.effects.get("appear", None)
        disappear_effect = self.effects.get("disappear", None)

        if None in [appear_effect, disappear_effect]:
            Trace.msg("<GameStore> can't find effects for scope CloseStore...")
        else:
            source.addEnable(disappear_effect)
            source.addPlay(disappear_effect, Wait=True)
            source.addDisable(disappear_effect)
            source.addEnable(appear_effect)
            source.addFunction(self.attachToEffect, "appear")
        source.addFunction(self.setEnableStore, False)

    def openFromAnywhere(self):
        if self.isStoreEnable() is False:
            return

        tc_open = TaskManager.createTaskChain()
        self.__tcs.append(tc_open)

        with tc_open as tc:
            tc.addScope(self.scopeOpenStore)
