from Foundation.DefaultManager import DefaultManager
from Foundation.GroupManager import GroupManager
from Foundation.System import System
from HOPA.Entities.BalanceIndicator.BalanceIndicator import ALIAS_ENV
from HOPA.Entities.BalanceIndicator.BalanceIndicator import EnergyIndicator
from HOPA.System.SystemEnergy import EVENT_UPDATE_TIMER

class SystemBalanceIndicator(System):

    def _onParams(self, params):
        self.update_timer_observer = None
        # settings:
        self.__alpha_time = DefaultManager.getDefaultFloat("BalanceIndicatorAlphaTime", 350.0)
        self.__trigger = DefaultManager.getDefaultTuple("BalanceIndicatorGroupTrigger", ["InGameMenu", "Store"], valueType=str)
        self.__timer_template = DefaultManager.getDefault("BalanceIndicatorEnergyTimerTemplate", "%02d:%02d:%02d")

    def _onRun(self):
        if GroupManager.hasGroup("BalanceIndicator") is False:
            return True
        if Mengine.hasTouchpad() is False:
            return True

        self.addObserver(Notificator.onLayerGroupEnable, self._cbLayerGroupEnable)
        self.addObserver(Notificator.onLayerGroupDisable, self._cbLayerGroupDisable)

        return True

    def _onStop(self):
        if self.update_timer_observer is not None:
            EVENT_UPDATE_TIMER.removeObserver(self.update_timer_observer)
            self.update_timer_observer = None

    def _cbLayerGroupEnable(self, group_name):
        if group_name not in self.__trigger:
            return False

        # TaskManager.runAlias("TaskSceneLayerGroupEnable", None, LayerName="BalanceIndicator", Value=True, Time=500.0)
        self.update_timer_observer = EVENT_UPDATE_TIMER.addObserver(self._cbUpdateTimer)

        if self.existTaskChain("SystemBalanceIndicator_Disappear") is True:
            self.removeTaskChain("SystemBalanceIndicator_Disappear")
        if self.existTaskChain("SystemBalanceIndicator_Appear") is True:
            self.removeTaskChain("SystemBalanceIndicator_Appear")
        with self.createTaskChain(Name="SystemBalanceIndicator_Appear", Repeat=False) as tc:
            tc.addTask("TaskSceneLayerGroupEnable", LayerName="BalanceIndicator", Value=True)
            tc.addTask("AliasObjectAlphaTo", GroupName="BalanceIndicator", ObjectName="Demon_BalanceIndicator", From=0.0, To=1.0, Time=self.__alpha_time)

        return False

    def _cbLayerGroupDisable(self, group_name):
        if group_name not in self.__trigger:
            return False

        if self.existTaskChain("SystemBalanceIndicator_Disappear") is True:
            self.removeTaskChain("SystemBalanceIndicator_Disappear")
        with self.createTaskChain(Name="SystemBalanceIndicator_Disappear", Repeat=False) as tc:
            tc.addTask("AliasObjectAlphaTo", GroupName="BalanceIndicator", ObjectName="Demon_BalanceIndicator", From=1.0, To=0.0, Time=self.__alpha_time)
            tc.addTask("TaskSceneLayerGroupEnable", LayerName="BalanceIndicator", Value=False)

        # TaskManager.runAlias("TaskSceneLayerGroupEnable", None, LayerName="BalanceIndicator", Value=False)
        EVENT_UPDATE_TIMER.removeObserver(self.update_timer_observer)
        self.update_timer_observer = None
        return False

    def _cbUpdateTimer(self, hours=0, minutes=0, seconds=0):
        timer = self.__timer_template % (hours, minutes, seconds)
        Mengine.setTextAliasArguments(ALIAS_ENV, EnergyIndicator.timer_text_alias, timer)
        return False