from Foundation.DemonManager import DemonManager
from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.MonetizationManager import MonetizationManager
from Foundation.Task.Semaphore import Semaphore
from Foundation.Utils import getCurrentPublisher, SimpleLogger


_Log = SimpleLogger("GiftExchange", enable=False)

PLATE_STATE_INPUT = 0
PLATE_STATE_FAIL = 1
PLATE_STATE_SUCCESS = 2


class GiftExchange(BaseEntity):
    # Aliases
    ALIAS_ENV = ""
    ALIAS_TEXT = "$GiftExchangeText"
    ALIAS_TITLE = "$GiftExchangeTitle"
    ALIAS_BUTTON = "$GiftExchangeButton"
    ALIAS_INPUT = "$GiftExchangeInput"
    ALIAS_REWARD = "$GiftExchangeReward"

    # Texts
    ID_TEXT_SUCCESS_TITLE = "ID_TEXT_GIFTEXCHANGE_SUCCESS_TITLE"
    ID_TEXT_SUCCESS_MSGS = {
        "MysteryChapter": "ID_TEXT_GIFTEXCHANGE_SUCCESS_MSG_CHAPTER",
        "chapter": "ID_TEXT_GIFTEXCHANGE_SUCCESS_MSG_CHAPTER",
        "force_chapter": "ID_TEXT_GIFTEXCHANGE_SUCCESS_MSG_CHAPTER",
        "golds": "ID_TEXT_GIFTEXCHANGE_SUCCESS_MSG_GOLD",
        "energy": "ID_TEXT_GIFTEXCHANGE_SUCCESS_MSG_ENERGY",
        "guide": "ID_TEXT_GIFTEXCHANGE_SUCCESS_MSG_GUIDE",
        "add_item": "ID_TEXT_GIFTEXCHANGE_SUCCESS_MSG_RECEIVE_ITEM",
    }
    ID_TEXT_FAIL_TITLE = "ID_TEXT_GIFTEXCHANGE_FAIL_TITLE"
    ID_TEXT_FAIL_MSG = "ID_TEXT_GIFTEXCHANGE_FAIL_MSG"
    ID_TEXT_INTERACT_GET = "ID_TEXT_GIFTEXCHANGE_INTERACT_GET"
    ID_TEXT_INTERACT_BACK = "ID_TEXT_GIFTEXCHANGE_INTERACT_BACK"
    ID_TEXT_INPUT_HELP = "ID_TEXT_GIFTEXCHANGE_INPUT_HELP"
    ID_TEXT_INPUT = "ID_TEXT_GIFTEXCHANGE_INPUT"
    ID_TEXT_EMPTY = "ID_EMPTY"
    ID_TEXT_LOADING = "ID_TEXT_LOADING"
    ID_TEXT_REWARD = "ID_TEXT_GIFTEXCHANGE_REWARD"

    # Movies
    MOVIE2_PLATE = "Movie2_GiftExchangePlate"
    MOVIE2_INPUT = "Movie2_GiftExchangeInput"
    MOVIE2BUTTON_INTERACT = "Movie2Button_GiftExchangeInteract"
    MOVIE2BUTTON_QUIT = "Movie2Button_GiftExchangeQuit"
    MOVIE2_REWARD = "Movie2_GiftExchangeReward"
    MOVIE2_EFFECT_APPEAR = "Movie2_GiftExchange_Appear"
    MOVIE2_EFFECT_DISAPPEAR = "Movie2_GiftExchange_Disappear"

    REQUEST_TIMEOUT = 10 * 1000.0
    LONG_TOUCH_DELAY = 2 * 1000.0

    def __init__(self):
        super(GiftExchange, self).__init__()
        self.editbox = None
        self.plate = None
        self.cancelLongTouchSemaphore = Semaphore(False, "cancelLongTouchSemaphore")

    def _onPreparation(self):
        if self.object.hasObject("Demon_EditBox_GiftExchange") is False:
            Trace.log("Entity", 0, "GiftExchange can't find object 'Demon_EditBox_GiftExchange' inside!!")
        self.editbox = self.object.getObject("Demon_EditBox_GiftExchange")

        self.__initText()

        self.plate = Plate(self)
        self.setActiveEditBox(False)

    def _onDeactivate(self):
        if self.plate is not None:
            self.plate.cleanUp()
            self.plate = None

        self.editbox = None

    # Scopes ///////////////////////////////////////////////////////////////////////////////////////////////////////////

    def scopeOpenPlate(self, source):
        appear_effect = self.plate.effects.get("appear", None)
        disappear_effect = self.plate.effects.get("disappear", None)
        interact_button = self.plate.content["interact"]

        source.addFunction(self.setActiveEditBox, False)

        source.addFunction(interact_button.setBlock, True)
        source.addFunction(self.__openPlate)

        if None in [appear_effect, disappear_effect]:
            Trace.msg("<GiftExchange> can't find effects for scope OpenPlate...")
        else:
            source.addEnable(appear_effect)
            source.addPlay(appear_effect, Wait=True)
            source.addDisable(appear_effect)
            source.addEnable(disappear_effect)
            if self.plate.current_effect != "disappear":
                source.addFunction(self.plate.attachToEffect, "disappear")

        source.addFunction(self.setActiveEditBox, True)
        source.addFunction(interact_button.setBlock, False)

    def scopeClosePlate(self, source):
        appear_effect = self.plate.effects.get("appear", None)
        disappear_effect = self.plate.effects.get("disappear", None)

        source.addFunction(self.setActiveEditBox, False)

        if None in [appear_effect, disappear_effect]:
            Trace.msg("<GiftExchange> can't find effects for scope ClosePlate...")
        else:
            source.addEnable(disappear_effect)
            source.addPlay(disappear_effect, Wait=True)
            source.addDisable(disappear_effect)
            source.addEnable(appear_effect)
            source.addFunction(self.plate.attachToEffect, "appear")
        source.addFunction(self.__closePlate)

    def scopeClickQuit(self, source):
        quit_button = self.plate.content["quit"]
        source.addTask("TaskMovie2ButtonClick", Movie2Button=quit_button)

    def scopeRun(self, source):
        interact_button = self.plate.content["interact"]

        # input or other plate
        with source.addIfTask(lambda: self.plate.state == PLATE_STATE_INPUT) as (tc_input, tc_other):
            tc_other.addFunction(self.setActiveEditBox, False)
            tc_other.addFunction(interact_button.setBlock, False)

            ###############################################

            tc_input.addFunction(self.setActiveEditBox, True)
            tc_input.addFunction(interact_button.setBlock, True)

            # input.addFunction(self.demon.setParam, "Value", u"")

            # editbox handler
            with tc_input.addRepeatTask() as (repeat, until):
                # react on input
                repeat.addScope(self.__scopeInputHandler)

                # wait click
                with until.addRaceTask(2) as (enter, click):
                    enter.addTask("TaskMovie2ButtonClick", Movie2Button=interact_button)
                    click.addTask("TaskKeyPress", Keys=[Mengine.KC_RETURN], isDown=True)

            tc_input.addFunction(self.setActiveEditBox, False)
            tc_input.addFunction(interact_button.setBlock, True)

            # request-respond handler
            tc_input.addScope(self.__scopeRequestRespondHandler)

            # click back button
            tc_input.addFunction(interact_button.setBlock, False)
            tc_input.addTask("TaskMovie2ButtonClick", Movie2Button=interact_button)

    # ///// Private Scopes /////////////////////////////////////////////////////////////////////////////////////////////

    def __scopeRequestRespondHandler(self, source):
        with source.addParallelTask(2) as (respond_handler, request):
            with respond_handler.addRaceTask(2) as (respond, timeout):
                respond.addListener(Notificator.onGiftExchangeRedeemResult, Filter=self.__gotRespondFilter)

                timeout.addScope(self.__scopeTimeoutWithEffects)
                timeout.addFunction(self.plate.setFail)

            request.addFunction(self.__sendRequest)

    def __scopeInputHandler(self, source):
        with source.addRaceTask(2) as (default, hold):
            with default.addParallelTask(2) as (edit, empty):
                edit.addTask("TaskListener", ID=Notificator.EditBoxChange)
                edit.addScope(self.__scopeOnEditBoxChange)
                edit.addSemaphore(self.cancelLongTouchSemaphore, To=True)

                empty.addTask("TaskListener", ID=Notificator.EditBoxEmpty)
                empty.addScope(self.__scopeOnEditBoxEmpty)
                empty.addSemaphore(self.cancelLongTouchSemaphore, To=True)

            # long touch can paste code from clipboard
            hold.addScope(self.__scopeLongTouch)

    def __scopeTimeoutWithEffects(self, source, custom_text=None):
        if custom_text is None:
            message = Mengine.getTextFromId(self.ID_TEXT_LOADING)
        else:
            message = custom_text

        def doEffect():
            n = 0
            while True:
                text = message + "." * (n % 4)
                Mengine.removeTextAliasArguments(GiftExchange.ALIAS_ENV, GiftExchange.ALIAS_INPUT)
                Mengine.setTextAliasArguments(GiftExchange.ALIAS_ENV, GiftExchange.ALIAS_INPUT, text)
                n += 1
                yield

        effect_iter = doEffect()

        source.addFunction(self.setActiveEditBox, False)
        with source.addRepeatTask() as (effect, stop):
            # run effect
            effect.addFunction(effect_iter.next)
            effect.addDelay(750)

            stop.addDelay(GiftExchange.REQUEST_TIMEOUT)

    def __scopeLongTouch(self, source):
        # todo: make it better (with holding) - https://wonderland-games.atlassian.net/browse/VAMP-42
        untilSemaphore = Semaphore(False, "untilSemaphore")
        pastedSemaphore = Semaphore(False, "pastedSemaphore")

        with source.addRaceTask(2) as (main, interrupt):
            with main.addRepeatTask() as (loop, until):
                loop.addTask("TaskListener", ID=Notificator.EditBoxFocus)
                loop.addDelay(self.LONG_TOUCH_DELAY)
                loop.addFunction(_Log, "Long touch")
                loop.addFunction(self.__paste)
                loop.addSemaphore(pastedSemaphore, To=True)
                loop.addSemaphore(untilSemaphore, To=True)

                until.addSemaphore(untilSemaphore, From=True, To=False)

            with interrupt.addRaceTask(2) as (interrupt_1, interrupt_2):
                interrupt_1.addSemaphore(self.cancelLongTouchSemaphore, From=True, To=False)
                interrupt_2.addSemaphore(pastedSemaphore, From=True, To=False)
                # interrupt_2.addTask("TaskListener", ID=Notificator.EditBoxUnhold)

            interrupt.addSemaphore(untilSemaphore, To=True)
            interrupt.addSemaphore(self.cancelLongTouchSemaphore, To=False)

    def __scopeOnEditBoxChange(self, source):
        interact_button = self.plate.content["interact"]

        source.addFunction(Mengine.setTextAliasArguments, GiftExchange.ALIAS_ENV, GiftExchange.ALIAS_INPUT, "")
        source.addFunction(interact_button.setBlock, False)

    def __scopeOnEditBoxEmpty(self, source):
        interact_button = self.plate.content["interact"]
        input_help = Mengine.getTextByKey(GiftExchange.ID_TEXT_INPUT_HELP)

        source.addFunction(Mengine.setTextAliasArguments, GiftExchange.ALIAS_ENV, GiftExchange.ALIAS_INPUT, input_help)
        source.addFunction(interact_button.setBlock, True)

    ######################################################

    def __onKeyboardFilter(self, state):
        pos_list = {
            True: (0.0, -180.0),
            False: (0.0, 0.0)
        }
        pos = pos_list.get(state, None)
        _Log("get push from Keyboard: {} -> {}".format(state, pos))

        if self.plate.state is None:
            _Log("   but window is not active")
            return False

        if pos is not None:
            # all UI (except editbox) attached to that movie when GiftExchange is enabled
            disappear_effect = self.plate.effects["disappear"]
            disappear_effect.setPosition(pos)
            self.editbox.setPosition(pos)

        return False

    def __paste(self):
        clipboard = self._getFromClipboard()

        if clipboard is not None:
            try:  # I'm not really sure about that
                code = unicode(clipboard)
            except UnicodeDecodeError as ex:
                code = "ERROR"
                if _DEVELOPMENT is True:
                    Trace.log("Entity", 0, "clipboard={!r} - {} - paste {!r}".format(clipboard, ex, code))

            max_len = self.editbox.getParam("TextLengthLimit")
            if max_len is not None and len(code) > max_len:
                code = code[:max_len]
            for s in code:
                self.editbox.entity.addSymbol(s)
            return True

        return False

    def _getFromClipboard(self):
        # todo: add here Mengine method that will get information from clipboard
        return ""

    def _getInputCode(self):
        code = self.editbox.getParam("Value")
        return code

    def __sendRequest(self):
        self._sendRequest()

    def _sendRequest(self):
        """ method must send request and get respond as listener to onGiftExchangeRedeemResult """
        code = self._getInputCode()
        Notification.notify(Notificator.onRequestPromoCodeResult, code)

    def __gotRespondFilter(self, reward_type, reward_amount):
        if reward_type is None:
            self.plate.setFail()
        else:
            self.plate.setSuccess(reward_type, reward_amount)
        return True

    def __openPlate(self):
        self.plate.setInput()

    def __closePlate(self):
        self.plate.disableAllMovies()
        Mengine.setTextAliasArguments(GiftExchange.ALIAS_ENV, GiftExchange.ALIAS_INPUT, "")
        self.setActiveEditBox(False)

    def __initText(self):
        self.editbox.setParam("Value", u"")
        Mengine.setTextAlias(self.ALIAS_ENV, self.ALIAS_TITLE, self.ID_TEXT_EMPTY)
        Mengine.setTextAlias(self.ALIAS_ENV, self.ALIAS_TEXT, self.ID_TEXT_EMPTY)
        Mengine.setTextAlias(self.ALIAS_ENV, self.ALIAS_BUTTON, self.ID_TEXT_INTERACT_GET)
        Mengine.setTextAlias(self.ALIAS_ENV, self.ALIAS_INPUT, self.ID_TEXT_INPUT)
        Mengine.setTextAlias(self.ALIAS_ENV, self.ALIAS_REWARD, self.ID_TEXT_EMPTY)

    def setActiveEditBox(self, state):
        self.__onKeyboardFilter(state)
        self.editbox.entity.setActive(state)


class Plate(object):

    def __init__(self, entity):
        self.entity = entity
        self.object = entity.object

        self.content = {}
        self.effects = {}
        self.current_effect = None

        self.icon = None
        self.icon_movie = None

        self.state = None

        self.__initMovies()

    def __initMovies(self):
        if self.object.hasObject(GiftExchange.MOVIE2_PLATE):
            self.content["plate"] = self.object.getObject(GiftExchange.MOVIE2_PLATE)
            self.content["plate"].setInteractive(True)
        if self.object.hasObject(GiftExchange.MOVIE2_INPUT):
            self.content["input"] = self.object.getObject(GiftExchange.MOVIE2_INPUT)
        if self.object.hasObject(GiftExchange.MOVIE2BUTTON_INTERACT):
            self.content["interact"] = self.object.getObject(GiftExchange.MOVIE2BUTTON_INTERACT)
        if self.object.hasObject(GiftExchange.MOVIE2BUTTON_QUIT):
            self.content["quit"] = self.object.getObject(GiftExchange.MOVIE2BUTTON_QUIT)
        if self.object.hasObject(GiftExchange.MOVIE2_REWARD):
            self.icon_movie = self.object.getObject(GiftExchange.MOVIE2_REWARD)

        if self.object.hasObject(GiftExchange.MOVIE2_EFFECT_APPEAR):
            self.effects["appear"] = self.object.getObject(GiftExchange.MOVIE2_EFFECT_APPEAR)
        if self.object.hasObject(GiftExchange.MOVIE2_EFFECT_DISAPPEAR):
            self.effects["disappear"] = self.object.getObject(GiftExchange.MOVIE2_EFFECT_DISAPPEAR)

        # _Log("loaded effects: {}, loaded content: {}".format(self.effects.keys(), self.content.keys()))

        content_slot = self.content["plate"].getMovieSlot("content")
        if content_slot is not None:
            nodes = [
                self.content["input"].getEntityNode(),
                self.content["interact"].getEntityNode(),
                self.content["quit"].getEntityNode(),
            ]
            if self.icon_movie is not None:
                nodes.append(self.icon_movie.getEntityNode())

            for node in nodes:
                content_slot.addChild(node)
        else:
            Trace.log("Entity", 0, "Plate.__initMovies: movie 'GiftExchangePlate' should has slot 'content'")

        self.attachToEffect("appear")  # default effect
        for movie in self.content.values():
            movie.setEnable(True)
        for movie in self.effects.values():
            movie.setEnable(False)

    def attachToEffect(self, effect):
        window_movie = self.content["plate"]
        effect_movie = self.effects.get(effect, None)
        if effect_movie is None:
            Trace.log("Entity", 0, "Plate.attachToEffect: can't find effect '{}' in self.effects dict={}".format(effect, self.effects))
            return

        slot = effect_movie.getMovieSlot("window")
        if slot is not None:
            window_node = window_movie.getEntityNode()
            window_node.removeFromParent()
            slot.addChild(window_node)
        else:
            Trace.log("Entity", 0, "Plate.attachToEffect: movie '{}' should has slot 'window'".format(effect_movie.getName()))
            return

        effect_movie.setLastFrame(False)  # set first frame
        self.current_effect = effect

    def disableAllMovies(self):
        for movie in self.content.values():
            movie.setEnable(False)
        self.state = None

    def setInput(self):
        self.reset()

        for movie in self.content.values():
            movie.setEnable(True)

        Mengine.setTextAlias(GiftExchange.ALIAS_ENV, GiftExchange.ALIAS_TITLE, GiftExchange.ID_TEXT_EMPTY)
        Mengine.removeTextAliasArguments(GiftExchange.ALIAS_ENV, GiftExchange.ALIAS_TEXT)
        Mengine.setTextAlias(GiftExchange.ALIAS_ENV, GiftExchange.ALIAS_TEXT, GiftExchange.ID_TEXT_EMPTY)
        Mengine.setTextAlias(GiftExchange.ALIAS_ENV, GiftExchange.ALIAS_BUTTON, GiftExchange.ID_TEXT_INTERACT_GET)
        input_help = Mengine.getTextByKey(GiftExchange.ID_TEXT_INPUT_HELP)
        Mengine.setTextAliasArguments(GiftExchange.ALIAS_ENV, GiftExchange.ALIAS_INPUT, input_help)

        self.state = PLATE_STATE_INPUT

    def setFail(self):
        self.content["input"].setEnable(False)

        Mengine.setTextAlias(GiftExchange.ALIAS_ENV, GiftExchange.ALIAS_TITLE, GiftExchange.ID_TEXT_FAIL_TITLE)
        Mengine.removeTextAliasArguments(GiftExchange.ALIAS_ENV, GiftExchange.ALIAS_TEXT)
        Mengine.setTextAlias(GiftExchange.ALIAS_ENV, GiftExchange.ALIAS_TEXT, GiftExchange.ID_TEXT_FAIL_MSG)
        Mengine.setTextAlias(GiftExchange.ALIAS_ENV, GiftExchange.ALIAS_BUTTON, GiftExchange.ID_TEXT_INTERACT_BACK)

        self.state = PLATE_STATE_FAIL

    def setSuccess(self, reward_type=None, reward_amount=None):
        self.content["input"].setEnable(False)

        Mengine.setTextAlias(GiftExchange.ALIAS_ENV, GiftExchange.ALIAS_TITLE, GiftExchange.ID_TEXT_SUCCESS_TITLE)
        Mengine.removeTextAliasArguments(GiftExchange.ALIAS_ENV, GiftExchange.ALIAS_TEXT)

        if reward_type not in GiftExchange.ID_TEXT_SUCCESS_MSGS:
            Trace.log("Entity", 0, "GiftExchange doesn't know reward_type {!r}".format(reward_type))
            Mengine.setTextAlias(GiftExchange.ALIAS_ENV, GiftExchange.ALIAS_TEXT, GiftExchange.ID_TEXT_EMPTY)
        else:
            reward_text_id = GiftExchange.ID_TEXT_SUCCESS_MSGS[reward_type]

            Mengine.setTextAlias(GiftExchange.ALIAS_ENV, GiftExchange.ALIAS_TEXT, reward_text_id)
            if "%s" in Mengine.getTextFromId(reward_text_id):
                Mengine.setTextAliasArguments(GiftExchange.ALIAS_ENV, GiftExchange.ALIAS_TEXT, str(reward_amount))

            self._setRewardInfo(reward_type, reward_amount)

        Mengine.setTextAlias(GiftExchange.ALIAS_ENV, GiftExchange.ALIAS_BUTTON, GiftExchange.ID_TEXT_INTERACT_BACK)

        self.state = PLATE_STATE_SUCCESS

    def _setRewardInfo(self, reward_type, reward_amount):
        if reward_type is None:
            return

        if self.icon_movie is None:
            return

        if self.icon_movie.hasMovieSlot("icon") is False:
            Trace.log("Entity", 0, "GiftExchange can't set reward info - slot 'icon' on {} not exists".format(self.icon_movie.getName()))
            return

        game_store_name = MonetizationManager.getGeneralSetting("GameStoreName", "GameStore")
        GameStore = DemonManager.getDemon(game_store_name)

        icon_references = {
            "golds": "Movie2_Coin_{}",
            "energy": "Movie2_Energy_{}"
        }

        if reward_type not in icon_references:
            Trace.log("Entity", 3, "GiftExchange._setRewardInfo doesn't know reward_type {!r}".format(reward_type))
            return

        icon_name = icon_references[reward_type].format(getCurrentPublisher())
        icon = GameStore.generateIcon("Icon", icon_name)
        icon_slot = self.icon_movie.getMovieSlot("icon")
        icon_slot.addChild(icon.getEntityNode())
        self.icon = icon

        icon.setEnable(True)

        Mengine.removeTextAliasArguments(GiftExchange.ALIAS_ENV, GiftExchange.ALIAS_REWARD)
        Mengine.setTextAlias(GiftExchange.ALIAS_ENV, GiftExchange.ALIAS_REWARD, GiftExchange.ID_TEXT_REWARD)
        Mengine.setTextAliasArguments(GiftExchange.ALIAS_ENV, GiftExchange.ALIAS_REWARD, str(reward_amount))

        self.icon_movie.setEnable(True)

    def reset(self):
        self.entity.editbox.setParam("Value", u"")

        if self.icon_movie is not None:
            self.icon_movie.setEnable(False)
        if self.icon is not None:
            self.icon.onDestroy()
            self.icon = None

    def cleanUp(self):
        self.reset()
        if self.icon_movie is not None:
            self.icon_movie.returnToParent()
