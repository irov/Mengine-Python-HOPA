from Foundation.DefaultManager import DefaultManager
from Foundation.DemonManager import DemonManager
from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.GroupManager import GroupManager
from Foundation.MonetizationManager import MonetizationManager
from Foundation.TaskManager import TaskManager
from Foundation.Utils import getCurrentPublisher
from Foundation.SystemManager import SystemManager
from Notification import Notification


ALIAS_ENV = ""


class BalanceIndicator(BaseEntity):

    @staticmethod
    def declareORM(Type):
        BaseEntity.declareORM(Type)
        Type.addAction(Type, "ShowGold",
                       Update=Functor(BalanceIndicator._cbUpdateShowIndicator, GoldIndicator.type.lower()))
        Type.addAction(Type, "ShowEnergy",
                       Update=Functor(BalanceIndicator._cbUpdateShowIndicator, EnergyIndicator.type.lower()))
        Type.addAction(Type, "ShowAdvertisement",
                       Update=Functor(BalanceIndicator._cbUpdateShowIndicator, AdvertisementIndicator.type.lower()))

    def __init__(self):
        super(BalanceIndicator, self).__init__()
        self.indicators = {}
        self.tc = None

    def __getIconProvider(self):
        provider = DefaultManager.getDefault("DefaultBalanceIndicatorIconProvider", "self")
        if provider == "current_store":
            provider = MonetizationManager.getGeneralSetting("GameStoreName", "GameStore")

        parent = None

        if provider != "self":
            if DemonManager.hasDemon(provider):
                parent = DemonManager.getDemon(provider)
            elif GroupManager.hasGroup(provider):
                parent = GroupManager.getGroup(provider)

        if parent is None:
            parent = self.object

        return parent

    def _onPreparation(self):
        self.indicators = {
            "gold": GoldIndicator(),
            "energy": EnergyIndicator(),
            "advertisement": AdvertisementIndicator(),
        }

        icon_provider_object = self.__getIconProvider()

        for indicator in self.indicators.values():
            indicator.prepare(self.object, icon_provider_object)
            indicator.setShow(self.object.getParam("Show" + indicator.type.title()))

    def _onActivate(self):
        self.tc = TaskManager.createTaskChain(Name="BalanceIndicatorHandler", Repeat=True)
        with self.tc as tc:
            for indicator, source_race in tc.addRaceTaskList(self.indicators.values()):
                source_race.addScope(indicator.scopeClick)
                source_race.addScope(indicator.scopeClicked)

    def _onDeactivate(self):
        if self.tc is not None:
            self.tc.cancel()
            self.tc = None

        for indicator in self.indicators.values():
            indicator.cleanUp()
        self.indicators = {}

    def _cbUpdateShowIndicator(self, state, indicator_type):
        indicator = self.indicators.get(indicator_type)
        if indicator is not None:
            indicator.setShow(state)


class IndicatorMixin(object):
    type = None
    icon_tag = None
    text_alias = None
    text_id = None
    identity = None

    if _DEVELOPMENT is True:
        def __repr__(self):
            return "<Indicator {}: {}>".format(self.type, self.__dict__)

    def __init__(self):
        self.bg_movie = None
        self.icon_movie = None
        self.observers = []

    def setShow(self, state):
        if self.bg_movie is not None:
            self.bg_movie.setEnable(state)

    def isShow(self):
        if self.bg_movie is not None:
            return self.bg_movie.getEnable() is True
        else:
            return False

    def prepare(self, parent, icon_provider_object):
        Mengine.setTextAlias(ALIAS_ENV, self.text_alias, self.text_id)
        self.refreshIndicatorText("load...")

        bg_name = "Movie2Button_{}Indicator".format(self.type)
        icon_name = "Movie2_{}_{}".format(self.icon_tag, getCurrentPublisher())

        if parent.hasObject(bg_name) is False:
            Trace.log("Entity", 0, "Indicator {!r} - not found object {!r} in {}".format(self.type, bg_name, parent.getName()))
            return False
        if icon_provider_object.hasPrototype(icon_name) is False:
            Trace.log("Entity", 0, "Indicator {!r} - not found prototype {!r} in {}".format(self.type, icon_name, icon_provider_object.getName()))
            return False

        bg_movie = parent.getObject(bg_name)
        try:
            icon_movie = icon_provider_object.generateIcon("Movie2_{}".format(self.type), icon_name, Enable=True)
        except AttributeError:
            icon_movie = icon_provider_object.generateObjectUnique("Movie2_{}".format(self.type), icon_name, Enable=True)

        icon_node = icon_movie.getEntityNode()
        icon_node.removeFromParent()
        # we can't do properly slot check, so just addChild and pray that it would be ok
        bg_movie.addChildToSlot(icon_node, "icon")
        # setShow will be called later

        self.bg_movie = bg_movie
        self.icon_movie = icon_movie

        self.observers = [
            Notification.addObserver(self.identity, self.refreshIndicatorText)
        ]

        return True

    def cleanUp(self):
        for observer in self.observers:
            Notification.removeObserver(observer)
        self.observers = []

        bg_movie = self.bg_movie
        icon_movie = self.icon_movie

        if bg_movie is not None:
            bg_movie.removeFromParentSlot(icon_movie.getEntityNode(), "icon")
            icon_movie.onDestroy()

        self.bg_movie = None
        self.icon_movie = None

    def refreshIndicatorText(self, balance):
        Mengine.setTextAliasArguments(ALIAS_ENV, self.text_alias, str(balance))
        return False

    def scopeClick(self, source):
        if self.bg_movie is not None:
            source.addTask("TaskMovie2ButtonClick", Movie2Button=self.bg_movie)
        else:
            source.addBlock()

    def scopeClicked(self, source):
        source.addNotify(Notificator.onIndicatorClicked, self.type)


class GoldIndicator(IndicatorMixin):
    type = "Gold"
    icon_tag = "Coin"
    text_alias = "$AliasGoldBalance"
    text_id = "ID_TEXT_GOLD_BALANCE"
    identity = Notificator.onUpdateGoldBalance


class EnergyIndicator(IndicatorMixin):
    type = "Energy"
    icon_tag = "Energy"
    text_alias = "$AliasEnergyBalance"
    text_id = "ID_TEXT_ENERGY_BALANCE"

    timer_text_id = "ID_TEXT_ENERGY_TIMER"
    timer_text_alias = "$AliasEnergyTimer"
    identity = Notificator.onUpdateEnergyBalance

    def __init__(self):
        super(EnergyIndicator, self).__init__()
        self.timer_movie = None
        self.timer_enable = False
        self.max_energy = None

    def _prepareDisable(self, parent, timer_movie):
        bg_name = "Movie2Button_{}Indicator".format(self.type)
        if parent.hasObject(bg_name) is False:
            return True
        bg_movie = parent.getObject(bg_name)
        bg_movie.setEnable(False)

        if timer_movie is not None:
            timer_movie.setEnable(False)
        return True

    def prepare(self, parent, icon_provider_object):
        timer_name = "Movie2_EnergyTimer"
        timer_movie = None
        if parent.hasObject(timer_name) is True:
            timer_movie = parent.getObject(timer_name)

        if SystemManager.hasSystem("SystemEnergy") is False:
            return self._prepareDisable(parent, timer_movie)

        SystemEnergy = SystemManager.getSystem("SystemEnergy")
        if SystemEnergy.isEnable() is False:
            return self._prepareDisable(parent, timer_movie)

        self.max_energy = SystemEnergy.getMaxEnergy()
        if super(EnergyIndicator, self).prepare(parent, icon_provider_object) is False:
            return False

        if timer_movie is not None:
            Mengine.setTextAlias(ALIAS_ENV, self.timer_text_alias, self.timer_text_id)
            default_text = DefaultManager.getDefault("BalanceIndicatorEnergyTimerDefaultText", "0:0:0")
            Mengine.setTextAliasArguments(ALIAS_ENV, self.timer_text_alias, default_text)

            timer_node = timer_movie.getEntityNode()
            timer_node.removeFromParent()
            self.bg_movie.addChildToSlot(timer_node, "timer")
            self.timer_movie = timer_movie

            self.timer_enable = SystemEnergy.in_recharging
            timer_movie.setEnable(self.timer_enable)
            timer_movie.setAlpha(1.0)

            self.observers.extend([
                Notification.addObserver(Notificator.onEnergyRecharge, self._cbRecharge),
                Notification.addObserver(Notificator.onEnergyCharged, self._cbCharged),
            ])
        else:
            Trace.log("Entity", 0, "Indicator {!r} - not found object {!r} in {}".format(
                self.type, timer_name, parent.getName()))

        return True

    def _cbRecharge(self):
        """ Observer when energy start recharge """
        self.timer_enable = True
        if self.isShow() is True:
            with TaskManager.createTaskChain(Name="BalanceIndicator_EnergyTimerHide") as tc:
                tc.addEnable(self.timer_movie)
                tc.addTask("AliasMovie2AlphaTo", Movie2=self.timer_movie, From=0.0, To=1.0, Time=350.0)
        else:
            self.timer_movie.setEnable(True)
        return False

    def _cbCharged(self):
        """ Observer when energy start charged """
        if self.timer_enable is False:
            return False
        if self.isShow() is True:
            with TaskManager.createTaskChain(Name="BalanceIndicator_EnergyTimerHide") as tc:
                tc.addEnable(self.timer_movie)
                tc.addTask("AliasMovie2AlphaTo", Movie2=self.timer_movie, From=1.0, To=0.0, Time=350.0)
                tc.addDisable(self.timer_movie)
        else:
            self.timer_movie.setEnable(False)
        self.timer_enable = False
        return False

    def cleanUp(self):
        if self.timer_movie is not None:
            timer_node = self.timer_movie.getEntityNode()
            self.bg_movie.removeFromParentSlot(timer_node, "timer")
            self.timer_movie.returnToParent()
            self.timer_movie = None

        super(EnergyIndicator, self).cleanUp()
        self.max_energy = None

    def refreshIndicatorText(self, balance):
        text = "{}/{}".format(balance, self.max_energy)
        Mengine.setTextAliasArguments(ALIAS_ENV, self.text_alias, text)
        return False


class AdvertisementIndicator(IndicatorMixin):
    type = "Advertisement"
    icon_tag = "AdvertisementReady"
    ad_name = "Rewarded"
    identity = Notificator.onAvailableAdsNew

    def prepare(self, parent, _):
        if MonetizationManager.getGeneralSetting("AdvertisementBalanceIndicatorEnable", False) is False:
            return True

        bg_name = "Movie2Button_{}Indicator".format(self.type)
        icon_name = "Movie2_{}_{}".format(self.icon_tag, getCurrentPublisher())

        if parent.hasObject(bg_name) is False:
            Trace.log("Entity", 0, "Indicator {!r} - not found object {!r} in {}".format(self.type, bg_name, parent.getName()))
            return False
        if parent.hasPrototype(icon_name) is False:
            Trace.log("Entity", 0, "Indicator {!r} - not found prototype {!r} in {}".format(self.type, icon_name, parent.getName()))
            return False

        bg_movie = parent.getObject(bg_name)
        try:
            icon_movie = parent.generateIcon("Movie2_{}".format(self.type), icon_name, Enable=True)
        except AttributeError:
            icon_movie = parent.generateObjectUnique("Movie2_{}".format(self.type), icon_name, Enable=True)

        icon_node = icon_movie.getEntityNode()
        icon_node.removeFromParent()
        # we can't do properly slot check, so just addChild and pray that it would be ok
        bg_movie.addChildToSlot(icon_node, "icon")
        bg_movie.setBlock(self._isAdsEnded() is True)
        bg_movie.setEnable(True)

        self.bg_movie = bg_movie
        self.icon_movie = icon_movie

        self.observers = [
            Notification.addObserver(Notificator.onAvailableAdsNew, self._cbAvailableAdsNew),
            Notification.addObserver(Notificator.onAvailableAdsEnded, self._cbAvailableAdsEnded),
        ]

        return True

    def _cbAvailableAdsNew(self, ad_name):
        if self.ad_name != ad_name:
            return False
        self.bg_movie.setBlock(False)
        return False

    def _cbAvailableAdsEnded(self, ad_name):
        if self.ad_name != ad_name:
            return False
        self.bg_movie.setBlock(True)
        return False

    def _isAdsEnded(self):
        if SystemManager.hasSystem("SystemMonetization") is False:
            Trace.log("Entity", 0, "SystemMonetization not found to check is Ads Ended!!")
            return True

        SystemMonetization = SystemManager.getSystem("SystemMonetization")
        return SystemMonetization.isAdsEnded(self.ad_name) is True

    def scopeClick(self, source):
        source.addBlock()
