from HOPA.Entities.BalanceIndicator.IndicatorMixin import IndicatorMixin
from Foundation.SystemManager import SystemManager
from Foundation.DefaultManager import DefaultManager
from Foundation.TaskManager import TaskManager


class EnergyIndicator(IndicatorMixin):
    type = "Energy"
    icon_tag = "Energy"
    text_alias = "$AliasEnergyBalance"
    text_id = "ID_TEXT_ENERGY_BALANCE"
    infinity_text_id = "ID_TEXT_ENERGY_INFINITY"
    prepare_load_text = ".../..."

    timer_movie_name = "Movie2_EnergyTimer"
    timer_text_id = "ID_TEXT_ENERGY_TIMER"
    timer_text_alias = "$AliasEnergyTimer"
    identity = Notificator.onUpdateEnergyBalance

    def __init__(self):
        super(EnergyIndicator, self).__init__()
        self.timer_movie = None
        self.timer_enable = False
        self.max_energy = None

    def isEnabled(self):
        if SystemManager.hasSystem("SystemEnergy") is False:
            return False

        SystemEnergy = SystemManager.getSystem("SystemEnergy")
        if SystemEnergy.isEnable() is False:
            return False

        return super(EnergyIndicator, self).isEnabled()

    def _prepareDisable(self, parent):
        if parent.hasObject(self.timer_text_alias) is True:
            timer_movie = parent.getObject(self.timer_movie_name)
            timer_movie.setEnable(False)
        return super(EnergyIndicator, self)._prepareDisable(parent)

    def prepare(self, parent, icon_provider_object):
        timer_movie = None
        if parent.hasObject(self.timer_movie_name) is True:
            timer_movie = parent.getObject(self.timer_movie_name)

        SystemEnergy = SystemManager.getSystem("SystemEnergy")
        self.max_energy = SystemEnergy.getMaxEnergy()
        if super(EnergyIndicator, self).prepare(parent, icon_provider_object) is False:
            return False

        if timer_movie is not None:
            Mengine.setTextAlias(self.alias_env, self.timer_text_alias, self.timer_text_id)
            default_text = DefaultManager.getDefault("BalanceIndicatorEnergyTimerDefaultText", "0:0:0")
            Mengine.setTextAliasArguments(self.alias_env, self.timer_text_alias, default_text)

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
                self.type, self.timer_movie_name, parent.getName()))

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
        if balance == "inf":
            Mengine.setTextAliasArguments(self.alias_env, self.text_alias, Mengine.getTextFromId(self.infinity_text_id))
            return True

        text = "{}/{}".format(balance, self.max_energy)
        Mengine.setTextAliasArguments(self.alias_env, self.text_alias, text)
        return False
