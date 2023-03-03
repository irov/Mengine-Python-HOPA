from Event import Event
from Foundation.DemonManager import DemonManager
from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.MonetizationManager import MonetizationManager
from Foundation.TaskManager import TaskManager
from Foundation.Utils import SimpleLogger
from Foundation.Utils import calcTime


_Log = SimpleLogger("LimitedPromo")
EVENT_TIMEOUT = Event("LimitedPromoTimeout")


class LimitedPromo(BaseEntity):
    TEXT_ID_TIMER = "ID_TEXT_LIMITED_PROMO_TIMER"
    ALIAS_TIMER = "$LimitedPromoTimer"

    @staticmethod
    def declareORM(Type):
        BaseEntity.declareORM(Type)
        Type.addAction(Type, "EndTimestamps")  # { tag: timestamp }
        Type.addAction(Type, "ActivatedProducts")  # { prod_id: timestamp }

    def __init__(self):
        super(LimitedPromo, self).__init__()
        self.tc = None

        self.params = {}
        self.content = None
        self.icons = {}
        self.effects = {}
        self.current_tag = None
        self.current_product_id = None

        self.timer = None
        self.unblock_timestamp = None

    def __loadParams(self):
        params = MonetizationManager.getSpecialPromotionParams()
        tagged = {param.tag: param for param in params.values() if param.limit_delay is not None}
        return tagged

    def _onPreparation(self):
        self.params = self.__loadParams()

        Mengine.setTextAlias("", self.ALIAS_TIMER, self.TEXT_ID_TIMER)
        Mengine.setTextAliasArguments("", self.ALIAS_TIMER, "0:0:0")

        self.__loadMovies()

    def _onActivate(self):
        self.refresh()

    def _onDeactivate(self):
        if self.tc is not None:
            self.tc.cancel()
            self.tc = None

        for icon in self.icons.values():
            icon.removeFromParent()
            icon.onDestroy()
        self.icons = {}

        self.content.returnToParent()
        self.content = None

        self.effects = {}

    # //////////

    def __loadMovies(self):
        def _getMovies(dict_in, dict_out):
            for key, movie_name in dict_in.items():
                if self.object.hasObject(movie_name):
                    movie = self.object.getObject(movie_name)
                    movie.setInteractive(True)
                    dict_out[key] = movie
                else:
                    _Log("{}:{} not inited ({} hasn't this object)".format(key, movie_name, self.object.getName()), err=True)

        if self.object.hasObject("Movie2_Content") is False:
            Trace.log("Entity", 0, "LimitedPromo: not found Movie2_Content")
            return False

        self.content = self.object.getObject("Movie2_Content")

        effects = {"appear": "Movie2_Appear", "disappear": "Movie2_Disappear", }
        _getMovies(effects, self.effects)

        icon_slot = None
        if self.content.hasSlot("icon") is False:
            Trace.log("Entity", 0, "LimitedPromo: can't attach icons - add slot 'icon' to Movie2_Content")
        else:
            icon_slot = self.content.getMovieSlot("icon")

        icons = {tag: "Movie2_Icon_" + tag for tag in self.params.keys()}
        icons["Default"] = "Movie2_Icon_Default"

        for tag, proto in icons.items():
            if self.object.hasPrototype(proto) is False:
                _Log("{}:{} not created ({} hasn't this prototype)".format(tag, proto, self.object.getName()), err=True)
                continue

            movie = self.object.generateObjectUnique(proto, proto, Enable=False)
            self.icons[tag] = movie

            if icon_slot is not None:
                node = movie.getEntityNode()
                icon_slot.addChild(node)

        self.attachToEffect("appear")
        self.setEnablePromo(False)

    def refresh(self):
        if len(self.EndTimestamps) == 0:
            return

        started_previously = self.EndTimestamps.items()
        prev_tag = started_previously[0][0]
        product = self.params[prev_tag]
        self.unblock_timestamp = self.getEndTimestamp(prev_tag)

        self.run(product.id)

    def setup(self, tag):
        if tag not in self.params:
            _Log("setup failed: wrong tag '{}'".format(tag), err=True)
            return False

        if self.current_tag is not None:
            icon = self.icons.get(tag)
            icon.setEnable(False)

        self.current_tag = tag

        icon = self.icons.get(tag)
        if icon is None:
            icon = self.icons.get("Default")
            _Log("setup has problem: not found icon for tag '{}'".format(tag), err=True)
        icon.setEnable(True)

        self.setTimer()

        return True

    # effects

    def scopeAppear(self, source):
        appear_effect = self.effects.get("appear", None)
        disappear_effect = self.effects.get("disappear", None)

        source.addFunction(self.setEnablePromo, True)
        if None in [appear_effect, disappear_effect]:
            _Log("can't find effects for scope Open...", err=True)
        else:
            source.addEnable(appear_effect)
            source.addPlay(appear_effect, Wait=True)
            source.addDisable(appear_effect)
            source.addEnable(disappear_effect)
            source.addFunction(self.attachToEffect, "disappear")

    def scopeDisappear(self, source):
        appear_effect = self.effects.get("appear", None)
        disappear_effect = self.effects.get("disappear", None)

        def _end():
            self.setEnablePromo(False)
            self.current_tag = None
            self.current_product_id = None
            self.removeTimer()
            self.unblock_timestamp = None

        if None in [appear_effect, disappear_effect]:
            _Log("can't find effects for scope Close...", err=True)
        else:
            source.addEnable(disappear_effect)
            source.addPlay(disappear_effect, Wait=True)
            source.addDisable(disappear_effect)
            source.addEnable(appear_effect)
            source.addFunction(self.attachToEffect, "appear")
        source.addFunction(_end)

    def attachToEffect(self, effect):
        effect_movie = self.effects.get(effect, None)
        if effect_movie is None:
            Trace.log("Entity", 0, "attachToEffect: can't find effect '{}' in self.effects {}".format(effect, self.effects.keys()))
            return

        slot = effect_movie.getMovieSlot("content")
        if slot is None:
            Trace.log("Entity", 0, "attachToEffect: movie '{}' should has slot 'content'".format(effect_movie.getName()))
            return

        node = self.content.getEntityNode()
        node.removeFromParent()
        slot.addChild(node)
        effect_movie.setLastFrame(False)  # set first frame

    # interact

    def run(self, prod_id):
        if self.tc is not None:
            return False

        params = MonetizationManager.getSpecialPromoById(prod_id)
        if params is None:
            _Log("run() aborted: start failed - not found product for id {}".format(prod_id), err=True)
            return False

        if DemonManager.hasDemon("SpecialPromotion") is False:
            _Log("run() aborted: requires demon SpecialPromotion!!! Read Confluence/.../SCR/pages/1795522563", err=True)
            return False

        if self.setup(params.tag) is False:
            return False
        self.current_product_id = prod_id

        if self.object.isActivated(prod_id):
            self.object.setActivatedProduct(prod_id)

        def _cb(isSkip):
            self.setEnablePromo(False)
            self.tc = None

        self.tc = TaskManager.createTaskChain(Name="LimitedPromotion", Cb=_cb)
        with self.tc as tc:
            tc.addScope(self.scopeAppear)

            SpecialPromotion = DemonManager.getDemon("SpecialPromotion")
            with tc.addRepeatTask() as (purchase, until):
                purchase.addScope(self.scopeClick)
                purchase.addFunction(SpecialPromotion.run, prod_id)

                with until.addRaceTask(2) as (timeout, purchased):
                    timeout.addEvent(EVENT_TIMEOUT)  # promotion ended
                    purchased.addListener(Notificator.onPaySuccess, Filter=lambda purchased_id: purchased_id == prod_id)
                    purchased.addFunction(self.object.endPromoByTag, self.current_tag)

            tc.addScope(self.scopeDisappear)

        return True

    def scopeClick(self, source):
        tag = self.current_tag
        icon = self.icons.get(tag)

        if icon is None:
            _Log("scopeClick blocked [{}]: no icon to click", err=True)
            source.addBlock()
            return

        if icon.hasSocket("socket") is False:
            _Log("scopeClick blocked [{}]: not found socket on icon {!r}".format(tag, icon.getName()), err=True)
            source.addBlock()
            return

        source.addTask("TaskMovie2SocketClick", Movie2=icon, SocketName="socket")

    # timer

    def setTimer(self):
        if self.timer is not None:
            Mengine.removeChronometer(self.timer)

        params = self.params[self.current_tag]
        delay = params.limit_delay
        if delay is None:
            _Log("Promo {!r} ({}) hasn't LimitDelay O_O, seTimer aborted".format(params.tag, params.id))
            Mengine.setTextAliasArguments("", self.ALIAS_TIMER, "")
            return

        if self.unblock_timestamp is not None:
            delay = Mengine.getTimeMs() / 1000 - delay
        _, hours, min, sec = calcTime(delay)

        # Mengine.removeTextAliasArguments("", self.ALIAS_TIMER)
        # Mengine.setTextAlias("", self.ALIAS_TIMER, self.TEXT_ID_TIMER)
        Mengine.setTextAliasArguments("", self.ALIAS_TIMER, "{}:{}:{}".format(hours, min, sec))

        if self.unblock_timestamp is None:
            self.setEndTimestamp(self.current_tag)
        self.timer = Mengine.addChronometer(self._onTimer)

    def removeTimer(self):
        if self.timer is None:
            return

        Mengine.removeChronometer(self.timer)
        self.timer = None

    def _onTimer(self, timer_id, timestamp):
        if timer_id != self.timer:
            return

        timestamp /= 1000

        _, hours, min, sec = calcTime(self.unblock_timestamp - timestamp)
        Mengine.setTextAliasArguments("", self.ALIAS_TIMER, "{}:{}:{}".format(hours, min, sec))
        if self.unblock_timestamp - timestamp <= 0:
            self.timeout()

    def timeout(self):
        self.removeTimer()
        self.EndTimestamps.pop(self.current_tag)
        EVENT_TIMEOUT()

    def getEndTimestamp(self, tag):
        """ :returns: ending timestamp for inputed `tag` """
        timestamp = self.EndTimestamps.get(tag)
        return timestamp

    def setEndTimestamp(self, tag):
        params = self.params[tag]
        delay = params.limit_delay
        timestamp = Mengine.getTimeMs() / 1000 + delay

        self.EndTimestamps[tag] = timestamp
        self.unblock_timestamp = timestamp

    # utils

    def setEnablePromo(self, state):
        self.content.setEnable(state)
        icon = self.icons.get(self.current_tag)
        if icon is not None:
            icon.setEnable(state)

    def hasActivePromoNow(self):
        return self.current_tag is not None

    def getActivePromoNow(self):
        """ returns product id """
        return self.current_product_id
