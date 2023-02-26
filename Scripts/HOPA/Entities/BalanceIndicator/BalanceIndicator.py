from Foundation.DefaultManager import DefaultManager
from Foundation.DemonManager import DemonManager
from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.GroupManager import GroupManager
from Foundation.MonetizationManager import MonetizationManager
from Foundation.TaskManager import TaskManager
from Foundation.Utils import getCurrentPublisher
from HOPA.System.SystemEnergy import SystemEnergy
from Notification import Notification

ALIAS_ENV = ""

class BalanceIndicator(BaseEntity):

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
        self.indicators = {"gold": GoldIndicator(), "energy": EnergyIndicator()}

        icon_provider_object = self.__getIconProvider()

        for indicator in self.indicators.values():
            indicator.prepare(self.object, icon_provider_object)

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
        self.indicators = None

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
        self.observer = None

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
        bg_movie.setEnable(True)

        self.bg_movie = bg_movie
        self.icon_movie = icon_movie

        self.observer = Notification.addObserver(self.identity, self.refreshIndicatorText)

        return True

    def cleanUp(self):
        bg_movie = self.bg_movie
        icon_movie = self.icon_movie

        if bg_movie is not None:
            bg_movie.removeFromParentSlot(icon_movie.getEntityNode(), "icon")
            icon_movie.onDestroy()

        self.bg_movie = None
        self.icon_movie = None

        Notification.removeObserver(self.observer)
        self.observer = None

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
        self.timer_charged_observer = None
        self.timer_recharge_observer = None
        self.timer_enable = False

    def prepare(self, parent, icon_provider_object):
        timer_name = "Movie2_EnergyTimer"
        timer_movie = None
        if parent.hasObject(timer_name) is True:
            timer_movie = parent.getObject(timer_name)

        if SystemEnergy.isEnable() is False:
            bg_name = "Movie2Button_{}Indicator".format(self.type)
            if parent.hasObject(bg_name) is False:
                return True
            bg_movie = parent.getObject(bg_name)
            bg_movie.setEnable(False)

            if timer_movie is not None:
                timer_movie.setEnable(False)
            return True

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

            self.timer_recharge_observer = Notification.addObserver(Notificator.onEnergyRecharge, self._cbRecharge)
            self.timer_charged_observer = Notification.addObserver(Notificator.onEnergyCharged, self._cbCharged)
        else:
            Trace.log("Entity", 0, "Indicator {!r} - not found object {!r} in {}".format(self.type, timer_name, parent.getName()))

        return True

    def _cbRecharge(self):
        """ Observer when energy start recharge """
        self.timer_enable = True
        with TaskManager.createTaskChain(Name="BalanceIndicator_EnergyTimerHide") as tc:
            tc.addEnable(self.timer_movie)
            tc.addTask("AliasMovie2AlphaTo", Movie2=self.timer_movie, From=0.0, To=1.0, Time=350.0)
        return False

    def _cbCharged(self):
        """ Observer when energy start charged """
        if self.timer_enable is False:
            return False
        with TaskManager.createTaskChain(Name="BalanceIndicator_EnergyTimerHide") as tc:
            tc.addEnable(self.timer_movie)
            tc.addTask("AliasMovie2AlphaTo", Movie2=self.timer_movie, From=1.0, To=0.0, Time=350.0)
            tc.addDisable(self.timer_movie)
        self.timer_enable = False
        return False

    def cleanUp(self):
        if self.timer_movie is not None:
            timer_node = self.timer_movie.getEntityNode()
            self.bg_movie.removeFromParentSlot(timer_node, "timer")
            self.timer_movie.returnToParent()
            self.timer_movie = None

        if self.timer_recharge_observer is not None:
            Notification.removeObserver(self.timer_recharge_observer)
            self.timer_recharge_observer = None

        if self.timer_charged_observer is not None:
            Notification.removeObserver(self.timer_charged_observer)
            self.timer_charged_observer = None

        super(EnergyIndicator, self).cleanUp()

    def refreshIndicatorText(self, balance):
        text = "{}/{}".format(balance, SystemEnergy.getMaxEnergy())
        Mengine.setTextAliasArguments(ALIAS_ENV, self.text_alias, text)
        return False