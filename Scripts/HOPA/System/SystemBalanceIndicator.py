from Foundation.DefaultManager import DefaultManager
from Foundation.GroupManager import GroupManager
from Foundation.DemonManager import DemonManager
from Foundation.System import System
from Foundation.SceneManager import SceneManager
from Foundation.MonetizationManager import MonetizationManager
from HOPA.Entities.BalanceIndicator.BalanceIndicator import EnergyIndicator, GoldIndicator, AdvertisementIndicator
from HOPA.System.SystemEnergy import EVENT_UPDATE_TIMER

class SystemBalanceIndicator(System):

    def _onParams(self, params):
        self.update_timer_observer = None
        # settings:
        self.__alpha_time = DefaultManager.getDefaultFloat("BalanceIndicatorAlphaTime", 350.0)
        self.__trigger = DefaultManager.getDefaultTuple("BalanceIndicatorGroupTrigger", ["InGameMenu", "Store"], valueType=str)
        self.__timer_template = DefaultManager.getDefault("BalanceIndicatorEnergyTimerTemplate", "%02d:%02d:%02d")
        self.__hide_on_Dialog = DefaultManager.getDefaultBool("BalanceIndicatorHideOnDialog", False) is True
        self.__hide_on_Mind = DefaultManager.getDefaultBool("BalanceIndicatorHideOnMind", False) is True
        self.__hide_on_Tip = DefaultManager.getDefaultBool("BalanceIndicatorHideOnTip", False) is True
        self.__show_on_Change = DefaultManager.getDefaultBool("BalanceIndicatorShowOnBalanceChange", False) is True
        self.__show_time = DefaultManager.getDefaultFloat("BalanceIndicatorShowTime", 1500.0) + self.__alpha_time

        self.__whitelist = {}
        self.__blacklist = {}
        indicator_types = (EnergyIndicator.type, GoldIndicator.type, AdvertisementIndicator.type)
        for _type in indicator_types:
            self.__whitelist[_type] = DefaultManager.getDefaultTuple("{}IndicatorWhitelist".format(_type),
                                                                     default=(), valueType=str)
            self.__blacklist[_type] = DefaultManager.getDefaultTuple("{}IndicatorBlacklist".format(_type),
                                                                     default=(), valueType=str)

    def _onRun(self):
        if MonetizationManager.isMonetizationEnable() is False:
            return True

        if GroupManager.hasGroup("BalanceIndicator") is False:
            return True

        if Mengine.hasTouchpad() is False:
            return True

        self.addObserver(Notificator.onLayerGroupEnable, self._cbLayerGroupEnable)
        self.addObserver(Notificator.onLayerGroupDisable, self._cbLayerGroupDisable)

        if self.__hide_on_Dialog is True:
            self.addObserver(Notificator.onDialogBoxShow, self._cbHideOnActionStart)
            self.addObserver(Notificator.onDialogBoxPlayComplete, self._cbHideOnActionComplete)

        if self.__hide_on_Mind is True:
            self.addObserver(Notificator.onMindShow, self._cbHideOnActionStart)
            self.addObserver(Notificator.onMindPlayComplete, self._cbHideOnActionComplete)

        if self.__hide_on_Tip is True:
            self.addObserver(Notificator.onTipShow, self._cbHideOnActionStart)
            self.addObserver(Notificator.onTipPlayComplete, self._cbHideOnActionComplete)

        if self.__show_on_Change is True:
            self.addObserver(GoldIndicator.identity, self._cbShowOnAction)
            self.addObserver(EnergyIndicator.identity, self._cbShowOnAction)
            self.addObserver(AdvertisementIndicator.identity, self._cbShowOnAction)

        BalanceIndicator = DemonManager.getDemon("BalanceIndicator")

        for indicator_type, group_list in self.__whitelist.items():
            if len(group_list) == 0:
                continue
            BalanceIndicator.setParam("Show" + indicator_type, False)
            self.addObserver(Notificator.onLayerGroupEnable, self._cbWhiteBlackListLayerGroupEnable,
                             group_list, indicator_type, "whitelist")
            self.addObserver(Notificator.onLayerGroupDisable, self._cbWhiteBlackListLayerGroupDisable,
                             group_list, indicator_type, "whitelist")

        for indicator_type, group_list in self.__blacklist.items():
            if len(group_list) == 0:
                continue
            self.addObserver(Notificator.onLayerGroupEnable, self._cbWhiteBlackListLayerGroupEnable,
                             group_list, indicator_type, "blacklist")
            self.addObserver(Notificator.onLayerGroupDisable, self._cbWhiteBlackListLayerGroupDisable,
                             group_list, indicator_type, "blacklist")

        return True

    def _onStop(self):
        if MonetizationManager.isMonetizationEnable() is False:
            return

        if GroupManager.hasGroup("BalanceIndicator") is False:
            return

        if Mengine.hasTouchpad() is False:
            return

        if self.update_timer_observer is not None:
            EVENT_UPDATE_TIMER.removeObserver(self.update_timer_observer)
            self.update_timer_observer = None

    # public

    def isIndicatorsActive(self):
        return self.update_timer_observer is not None

    def toggleIfPossible(self, state):
        if state is True and self.isIndicatorsActive() is False:
            self._appearIndicators()
        elif state is False and self.isIndicatorsActive() is True:
            self._disappearIndicators()

    def tempShowIfPossible(self):
        if SceneManager.isCurrentGameScene() is False:
            return False

        if self.isIndicatorsActive() is True:
            return False

        if self.existTaskChain("SystemBalanceIndicator_TempShow") is True:
            self.removeTaskChain("SystemBalanceIndicator_TempShow")
        with self.createTaskChain(Name="SystemBalanceIndicator_TempShow", Repeat=False) as tc:
            tc.addFunction(self._appearIndicators)
            tc.addDelay(self.__show_time)
            tc.addFunction(self._disappearIndicators)

        return False

    # observers

    def _cbLayerGroupEnable(self, group_name):
        if group_name not in self.__trigger:
            return False

        self._appearIndicators()
        return False

    def _cbLayerGroupDisable(self, group_name):
        if group_name not in self.__trigger:
            return False

        self._disappearIndicators()
        return False

    def _cbHideOnActionComplete(self, *args, **kwargs):
        self.toggleIfPossible(True)
        return False

    def _cbHideOnActionStart(self, *args, **kwargs):
        self.toggleIfPossible(False)
        return False

    def _cbShowOnAction(self, *args, **kwargs):
        self.tempShowIfPossible()
        return False

    def _cbWhiteBlackListLayerGroupEnable(self, group_name, target_groups_name, indicator_type, mode):
        """ mode = blacklist || whitelist """

        if group_name not in target_groups_name:
            return False

        BalanceIndicator = DemonManager.getDemon("BalanceIndicator")

        if mode == "blacklist":
            BalanceIndicator.setParam("Show" + indicator_type, False)
        elif mode == "whitelist":
            BalanceIndicator.setParam("Show" + indicator_type, True)
        else:
            Trace.log("System", 0, "{} [{}] ERROR: unknown mode: {}".format(indicator_type, target_groups_name, mode))
            return True

        return False

    def _cbWhiteBlackListLayerGroupDisable(self, group_name, target_groups_name, indicator_type, mode):
        """ mode = blacklist || whitelist """

        if group_name not in target_groups_name:
            return False

        BalanceIndicator = DemonManager.getDemon("BalanceIndicator")

        if mode == "blacklist":
            BalanceIndicator.setParam("Show" + indicator_type, True)
        elif mode == "whitelist":
            BalanceIndicator.setParam("Show" + indicator_type, False)
        else:
            Trace.log("System", 0, "{} [{}] ERROR: unknown mode: {}".format(indicator_type, target_groups_name, mode))
            return True

        return False

    # utils

    def _appearIndicators(self):
        self.update_timer_observer = EVENT_UPDATE_TIMER.addObserver(self._cbUpdateTimer)

        if self.existTaskChain("SystemBalanceIndicator_Disappear") is True:
            self.removeTaskChain("SystemBalanceIndicator_Disappear")
        if self.existTaskChain("SystemBalanceIndicator_Appear") is True:
            self.removeTaskChain("SystemBalanceIndicator_Appear")

        with self.createTaskChain(Name="SystemBalanceIndicator_Appear", Repeat=False) as tc:
            tc.addTask("TaskSceneLayerGroupEnable", LayerName="BalanceIndicator", Value=True)
            tc.addTask("AliasObjectAlphaTo", GroupName="BalanceIndicator", ObjectName="Demon_BalanceIndicator",
                       From=0.0, To=1.0, Time=self.__alpha_time)

    def _disappearIndicators(self):
        if self.existTaskChain("SystemBalanceIndicator_Disappear") is True:
            self.removeTaskChain("SystemBalanceIndicator_Disappear")

        with self.createTaskChain(Name="SystemBalanceIndicator_Disappear", Repeat=False) as tc:
            tc.addTask("AliasObjectAlphaTo", GroupName="BalanceIndicator", ObjectName="Demon_BalanceIndicator",
                       From=1.0, To=0.0, Time=self.__alpha_time)
            tc.addTask("TaskSceneLayerGroupEnable", LayerName="BalanceIndicator", Value=False)

        EVENT_UPDATE_TIMER.removeObserver(self.update_timer_observer)
        self.update_timer_observer = None

    def _cbUpdateTimer(self, hours=0, minutes=0, seconds=0):
        timer = self.__timer_template % (hours, minutes, seconds)
        Mengine.setTextAliasArguments(EnergyIndicator.alias_env, EnergyIndicator.timer_text_alias, timer)
        return False
