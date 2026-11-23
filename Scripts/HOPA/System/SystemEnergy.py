from Foundation.PolicyManager import PolicyManager
from Foundation.SceneManager import SceneManager
from Foundation.SecureStringValue import SecureStringValue
from Foundation.System import System
from Foundation.SystemManager import SystemManager
from Foundation.Systems.SystemAnalytics import SystemAnalytics
from Foundation.Utils import SimpleLogger, calcTime
from HOPA.EnigmaManager import EnigmaManager
from HOPA.TransitionManager import TransitionManager
from Notification import Notification

_Log = SimpleLogger("SystemEnergy", option="energy")

EVENT_UPDATE_TIMER = Event("onEnergyTimerUpdate")
ACTION_NAMES = [
    "PickItem"
    , "CombineItems"
    , "PlaceItem"
    , "EnterHOG"
    , "FindHO"
    , "FitHO"
    , "DragDropItem"
]
ENERGY_INFINITY_CODE = "inf"
ENERGY_RECHARGE_VERSION = "1"
RECHARGE_TIMING_KEYS = ("max_energy", "refill_time", "refill_per_time")


class SystemEnergy(System):
    s_settings = {}  # key-value energy params
    s_actions = {}  # { action_name: true/false } - is action enable
    s_actions_price = {}  # { action_name: int price } - how many energy would be withdrawn

    in_recharging = False
    in_free_mode = False        # consume method always return True if free mode is True
    in_infinity_mode = False    # free mode, but shows it for user

    s_paid_enigmas = None

    def __init__(self):
        super(SystemEnergy, self).__init__()
        self.current_energy = None
        self.cooldown_timestamp = None  # time of the next refill
        self.timer = None

    @staticmethod
    def isEnable():
        return SystemEnergy.s_settings.get("enable", False)

    def _onInitialize(self):
        if Mengine.getConfigBool("Energy", "Enable", False) is False:
            return

        SystemEnergy.s_paid_enigmas = SecureStringValue("EnergyPaidEnigmas", "")

        settings = {
            "enable": True,
            "max_energy": Mengine.getConfigInt("Energy", "MaxEnergy", 300),
            "default_energy_consumption": Mengine.getConfigInt("Energy", "DefaultConsumption", 6),
            "refill_per_time": Mengine.getConfigInt("Energy", "RefillEnergyPerTime", 1),
            "refill_time": Mengine.getConfigFloat("Energy", "RefillTime", 240.0),
        }

        for key, default in (("max_energy", 300), ("refill_per_time", 1), ("refill_time", 240.0)):
            value = settings[key]
            if value <= 0 or value - value != 0:
                settings[key] = default

        actions = {
            action: Mengine.getConfigBool("Energy", action, False) for action in ACTION_NAMES
        }
        prices = {
            action: Mengine.getConfigInt("Energy", (action + "Consumption"), settings["default_energy_consumption"])
            for action in ACTION_NAMES
        }

        SystemEnergy.s_settings = settings
        SystemEnergy.s_actions = actions
        SystemEnergy.s_actions_price = prices

        self.debugCheats()
        self.__addDevToDebug()

        self.__initSaveProgress()

    def _onFinalize(self):
        self.removeTimer()
        self.__remDevToDebug()
        SystemEnergy.s_paid_enigmas = None

    def _onRun(self):
        if Mengine.hasTouchpad() is False:
            return True

        if Mengine.getConfigBool("Energy", "Enable", False) is False:
            return True

        self._setupInitialCurrentEnergy()

        self.setPolicies()
        self.setObservers()
        self.addAnalytics()
        return True

    def _setupInitialCurrentEnergy(self):
        if self.current_energy is None:
            self.current_energy = SystemEnergy.getMaxEnergy()

    def setObservers(self):
        self.addObserver(Notificator.onGetRemoteConfig, self._cbGetRemoteConfig)
        self.addObserver(Notificator.onEnergyIncrease, self.addEnergy)
        self.addObserver(Notificator.onEnergyDecrease, self.withdrawEnergy)
        self.addObserver(Notificator.onEnergySet, self.setEnergy)
        self.addObserver(Notificator.onLayerGroupEnable, self._cbLayerGroupEnable)
        if self.s_actions["EnterHOG"] is True:
            self.addObserver(Notificator.onSceneActivate, self._cbSceneActivate)
            self.addObserver(Notificator.onSceneDeactivate, self._cbSceneDeactivate)

    def _cbGetRemoteConfig(self, key, value):
        if key.startswith("energy_") is False:
            return False
        setting = key[len("energy_"):]
        if setting == "enable":
            return False

        values = self.s_settings if setting in self.s_settings else self.s_actions_price
        if setting not in values:
            return False

        previous = values[setting]
        try:
            updated = type(previous)(value)
        except (TypeError, ValueError, OverflowError):
            Trace.msg_err("SystemEnergy cannot apply {!r}: invalid value {!r}".format(key, value))
            return False

        if setting not in RECHARGE_TIMING_KEYS:
            values[setting] = updated
            return False

        if updated <= 0 or updated - updated != 0:
            Trace.msg_err("SystemEnergy cannot apply {!r}: expected positive finite value".format(key))
            return False
        if updated == previous:
            return False

        if self.current_energy is None or Mengine.hasCurrentAccount() is False:
            values[setting] = updated
        else:
            self.__updateRecharge(self._getTimestamp(), setting, updated)

        return False

    def _cbLayerGroupEnable(self, group_name):  # todo: remove hardcode notify from this system
        if group_name == "BalanceIndicator":
            self.notifyUpdateBalance()
        return False

    def setPolicies(self):
        if self.checkAction("PickItem") is True:
            PolicyManager.setPolicy("ClickItem", "PolicyEnergyClickItem")

    def addAnalytics(self):
        def _getExtraParams():
            return {"current_energy": self.current_energy}

        SystemAnalytics.addExtraAnalyticParams(_getExtraParams)

        SystemAnalytics.addAnalytic("refill_energy", Notificator.onEnergyIncrease, service_key="earn_currency",
                                    params_method=lambda amount: {'name': 'energy', 'amount': amount})
        SystemAnalytics.addAnalytic("consume_energy", Notificator.onEnergyConsumed, service_key="spent_currency",
                                    params_method=lambda action, amount: {'amount': amount, 'description': action, 'name': 'energy'})

        SystemAnalytics.addAnalytic("not_enough_energy", Notificator.onEnergyNotEnough, None,
                                    lambda action, value: {"action": action, "price": value})

    def _onStop(self):
        self.removeTimer()

    # === Enigma handling ==============================================================================================

    # observers

    def _cbSceneActivate(self, scene_name):
        if "HO" in scene_name:
            self._handlePaidEnigmaActivate(scene_name)

        return False

    def _cbSceneDeactivate(self, scene_name):
        if "HO" in scene_name:
            SystemEnergy.setFreeMode(False)

        return False

    # handle method

    def _handlePaidEnigmaActivate(self, name):
        enigma_id = None
        if EnigmaManager.hasEnigma(name):
            enigma_params = EnigmaManager.getEnigma(name)
            enigma_id = enigma_params.id

        if self.isEnigmaPaid(name, enigma_id) is True:
            SystemEnergy.setFreeMode(True)
            return

        action_name = "EnterHOG"

        if self.consume(action_name, notify_not_enough_energy=False) is True:
            self._savePaidEnigma(name, enigma_id)
            SystemEnergy.setFreeMode(True)
        else:
            current_scene_name = SceneManager.getCurrentSceneName()
            prev_game_scene_name = TransitionManager.getTransitionBack(current_scene_name)
            action_value = self.getActionEnergy(action_name)

            if self.existTaskChain("SystemEnergyHandleEnterHOG"):
                self.removeTaskChain("SystemEnergyHandleEnterHOG")
            with self.createTaskChain(Name="SystemEnergyHandleEnterHOG") as tc:
                tc.addNextFrame()  # finish scene activation before returning to the previous scene
                tc.addFunction(TransitionManager.changeScene, prev_game_scene_name)
                tc.addListener(Notificator.onSceneInit, Filter=lambda scene_name: scene_name == prev_game_scene_name)
                tc.addNotify(Notificator.onEnergyNotEnough, action_name, action_value)

            _Log("Not enough energy to play this game - transit to prev scene :(")
        pass

    # utils

    @staticmethod
    def isEnigmaPaid(enigma_name, enigma_id=None):
        raw_paid_enigmas = SystemEnergy.s_paid_enigmas.getValue()
        paid_enigmas = raw_paid_enigmas.split(";")

        is_paid = enigma_name in paid_enigmas or enigma_id in paid_enigmas

        _Log("-- isEnigmaPaid {!r} [{}] in {}: {}"
             .format(enigma_name, enigma_id, paid_enigmas, is_paid), optional=True)

        return is_paid

    @staticmethod
    def _savePaidEnigma(enigma_name, enigma_id=None):
        paid_enigmas = SystemEnergy.s_paid_enigmas.getValue()
        sep = ";" if len(paid_enigmas) != 0 else ""
        paid_enigmas += "%s%s" % (sep, enigma_id or enigma_name)

        SystemEnergy.s_paid_enigmas.setValue(paid_enigmas)

        save = SystemEnergy.s_paid_enigmas.getSave()
        Mengine.changeCurrentAccountSetting("EnergyPaidEnigmas", unicode(save))
        Mengine.saveAccounts()

    @staticmethod
    def _loadPaidEnigmas():
        save = str(Mengine.getCurrentAccountSetting("EnergyPaidEnigmas"))
        SystemEnergy.s_paid_enigmas.loadSave(save)

        _Log("------- EnergyPaidEnigmas: {!r} ({})"
             .format(SystemEnergy.s_paid_enigmas.getValue(), save), optional=True)

    # === Energy =======================================================================================================

    @staticmethod
    def setFreeMode(state):
        SystemEnergy.in_free_mode = bool(state)

    @staticmethod
    def isFreeMode():
        return SystemEnergy.in_free_mode is True

    def setInfinityMode(self, state):
        SystemEnergy.in_infinity_mode = state
        if self.isAccountEnergyInfinity() is not state:
            SystemEnergy.setAccountEnergyInfinity(state)

        if state is True:
            self.__applyProgress(self.current_energy, None, self._getTimestamp(), save=False)
        else:
            self.notifyUpdateBalance()

    @staticmethod
    def isInfinityMode():
        system_state = SystemEnergy.in_infinity_mode
        if system_state is True:
            _Log("Infinity Energy Mode")
        return system_state

    @staticmethod
    def setAccountEnergyInfinity(state):
        Mengine.changeCurrentAccountSettingBool("EnergyInfinity", state)
        Mengine.saveAccounts()

    @staticmethod
    def isAccountEnergyInfinity():
        is_energy_infinity = Mengine.getCurrentAccountSettingBool("EnergyInfinity")
        return is_energy_infinity

    @staticmethod
    def getMaxEnergy():
        return SystemEnergy.s_settings["max_energy"]

    @staticmethod
    def hasActionEnergy(action_name):
        return action_name in SystemEnergy.s_actions

    @staticmethod
    def getActionEnergy(action_name):
        return SystemEnergy.s_actions_price[action_name]

    @staticmethod
    def checkAction(action_name):
        return SystemEnergy.s_actions.get(action_name, False)

    def performAction(self, action_name):
        if Mengine.hasTouchpad() is False:
            return True
        if self.checkAction(action_name) is False:
            # action not enabled in configs.json
            return True
        if self.consume(action_name) is True:
            return True
        # user has not enough energy to perform action
        return False

    def isEnoughEnergy(self, energy):
        energy_left = self.current_energy - energy
        _Log("isEnoughEnergy [{}] {} - {} = {}"
             .format(energy_left >= 0, self.current_energy, energy, energy_left), optional=True)
        if energy_left < 0:
            return False
        return True

    def withdrawEnergy(self, energy):
        if self.isInfinityMode() is True:
            return False

        self.__changeEnergy(max(0, self.current_energy - energy))
        return False

    def addEnergy(self, energy):
        if self.isInfinityMode() is True:
            return False

        self.__changeEnergy(self.current_energy + energy)
        return False

    def preparePurchaseEnergy(self, transaction, amount, infinity=False):
        if self.isInfinityMode() is True and self.isAccountEnergyInfinity() is True:
            return True

        energy = int(transaction.getSetting("Energy", self.current_energy))
        cooldown = self.__parseCooldown(transaction.getSetting("EnergyCooldown", self.cooldown_timestamp))
        timestamp = self._getTimestamp()
        gained, cooldown = self.__getRechargeTicks(energy, cooldown, timestamp)
        energy += gained + amount
        if infinity is True:
            transaction.setSetting("EnergyInfinity", "true")
            energy = max(energy, self.getMaxEnergy())

        cooldown = self.__getRechargeCooldown(energy, cooldown, timestamp)
        settings = self.__makeProgressSettings(energy, cooldown, timestamp)
        for key, value in settings.iteritems():
            transaction.setSetting(key, value)

        transaction.afterCommit(self._applyPurchaseEnergy, transaction.settings)
        return True

    def _applyPurchaseEnergy(self, settings):
        if settings.get("EnergyInfinity") == "true":
            SystemEnergy.in_infinity_mode = True

        energy = int(settings["Energy"])
        cooldown = self.__parseCooldown(settings["EnergyCooldown"])
        timestamp = int(settings["EnergyLastSave"])
        self.__applyProgress(energy, cooldown, timestamp, save=False)

    def setEnergy(self, energy):
        if energy == ENERGY_INFINITY_CODE:
            self.setInfinityMode(True)
            return False

        self.__changeEnergy(max(0, energy))
        return False

    def __changeEnergy(self, energy):
        if energy == self.current_energy:
            return

        self.__applyProgress(energy, self.cooldown_timestamp, self._getTimestamp())

    def consume(self, action_name, notify_not_enough_energy=True):
        """ Used for paid actions that depends on own system energy.
            Checks free mode, so user can not pay energy if it is enabled.

            :returns: `True` if payment success (or was free mode), `False` if not enough energy.
        """
        if SystemEnergy.isFreeMode() is True:
            return True

        if SystemEnergy.isInfinityMode() is True:       # user bought infinity energy
            return True

        action_value = self.getActionEnergy(action_name)
        return self.payEnergy(action_value, action_name, notify_not_enough_energy)

    def payEnergy(self, amount, action_name, notify_not_enough_energy=True):
        """ Performs actual payment with energy. [!] Ignores free mode.

            :returns: `True` if payment success, `False` if not enough energy.
        """
        if SystemEnergy.isInfinityMode() is True:       # user bought infinity energy
            Notification.notify(Notificator.onEnergyConsumed, action_name, 0)
            return True

        if self.isEnoughEnergy(amount) is False:
            if notify_not_enough_energy is True:
                Notification.notify(Notificator.onEnergyNotEnough, action_name, amount)
            return False

        self.withdrawEnergy(amount)
        Notification.notify(Notificator.onEnergyConsumed, action_name, amount)
        return True

    def notifyUpdateBalance(self):
        if self.in_infinity_mode is True:
            Notification.notify(Notificator.onUpdateEnergyBalance, ENERGY_INFINITY_CODE)
            return
        Notification.notify(Notificator.onUpdateEnergyBalance, self.current_energy)

    # === Refill =======================================================================================================

    def __getRechargeCooldown(self, energy, cooldown, timestamp):
        if energy >= self.getMaxEnergy():
            return None
        if cooldown is None:
            return timestamp + self.s_settings["refill_time"]
        return cooldown

    def __getRefillEnd(self, energy, cooldown):
        missing = self.getMaxEnergy() - energy
        per_tick = self.s_settings["refill_per_time"]
        ticks_to_full = (missing + per_tick - 1) // per_tick
        return cooldown + (ticks_to_full - 1) * self.s_settings["refill_time"]

    def getSecondsToFullEnergy(self):
        energy = self.current_energy
        if energy is None or self.in_infinity_mode is True or energy >= self.getMaxEnergy():
            return 0

        timestamp = self._getTimestamp()
        cooldown = self.__getRechargeCooldown(energy, self.cooldown_timestamp, timestamp)
        return max(0, self.__getRefillEnd(energy, cooldown) - timestamp)

    def __getRechargeTicks(self, energy, cooldown, timestamp):
        if cooldown is None or timestamp < cooldown:
            return 0, cooldown

        remaining = self.getMaxEnergy() - energy
        if remaining <= 0:
            return 0, None
        if timestamp >= self.__getRefillEnd(energy, cooldown):
            return remaining, None

        interval = self.s_settings["refill_time"]
        ticks = 1 + int((timestamp - cooldown) // interval)
        gained = min(remaining, ticks * self.s_settings["refill_per_time"])
        return gained, cooldown + ticks * interval

    def __updateRecharge(self, timestamp, setting=None, value=None):
        gained = 0
        cooldown = self.cooldown_timestamp
        if self.in_infinity_mode is False:
            gained, cooldown = self.__getRechargeTicks(self.current_energy, cooldown, timestamp)

        if setting is not None:
            self.s_settings[setting] = value

        energy = self.current_energy + gained
        if gained > 0 and self.isRun() is True:
            # addEnergy saves the balance with this deadline before the analytics observer runs.
            self.cooldown_timestamp = self.__getRechargeCooldown(energy, cooldown, timestamp)
            Notification.notify(Notificator.onEnergyIncrease, gained)
            return

        self.__applyProgress(energy, cooldown, timestamp)

    def __applyProgress(self, energy, cooldown, timestamp, save=True):
        self.current_energy = energy
        self.cooldown_timestamp = None if self.in_infinity_mode is True else self.__getRechargeCooldown(energy, cooldown, timestamp)

        was_recharging = self.timer is not None
        recharging = self.cooldown_timestamp is not None
        if recharging is False:
            self.removeTimer()
        elif was_recharging is False:
            self.timer = Mengine.addChronometer(self._onTimer)
        SystemEnergy.in_recharging = recharging

        if save is True:
            self.__saveProgress(timestamp)

        if was_recharging != recharging:
            event = Notificator.onEnergyRecharge if recharging is True else Notificator.onEnergyCharged
            Notification.notify(event)

        self.notifyUpdateBalance()

    def _onTimer(self, time):
        if self.timer is None:
            return

        timestamp = self._getTimestamp()
        if timestamp >= self.cooldown_timestamp:
            self.__updateRecharge(timestamp)

        if self.cooldown_timestamp is None:
            return

        _, hours, minutes, seconds = calcTime(max(0, self.cooldown_timestamp - timestamp))
        EVENT_UPDATE_TIMER(hours, minutes, seconds)

    def removeTimer(self):
        if self.timer is None:
            return

        Mengine.removeChronometer(self.timer)
        self.timer = None
        SystemEnergy.in_recharging = False

    # === Save\Load ====================================================================================================

    @staticmethod
    def __makeProgressSettings(energy, cooldown, timestamp):
        return {
            "Energy": energy,
            "EnergyCooldown": cooldown,
            "EnergyLastSave": timestamp,
            "EnergyRechargeVersion": ENERGY_RECHARGE_VERSION,
        }

    @staticmethod
    def __parseCooldown(value):
        if value in (None, "", "None"):
            return None

        try:
            cooldown = float(value)
        except (TypeError, ValueError, OverflowError):
            return None

        if cooldown <= 0 or cooldown - cooldown != 0:
            return None
        return cooldown

    def __saveProgress(self, timestamp):
        settings = self.__makeProgressSettings(self.current_energy, self.cooldown_timestamp, timestamp)
        for key, value in settings.iteritems():
            Mengine.changeCurrentAccountSetting(key, unicode(value))

        Mengine.saveAccounts()

    def __loadProgress(self):
        timestamp = self._getTimestamp()
        try:
            energy = int(Mengine.getCurrentAccountSetting("Energy"))
        except (TypeError, ValueError, OverflowError):
            energy = self.getMaxEnergy()

        try:
            save_time = int(Mengine.getCurrentAccountSetting("EnergyLastSave"))
        except (TypeError, ValueError, OverflowError):
            save_time = timestamp

        cooldown = self.__parseCooldown(Mengine.getCurrentAccountSetting("EnergyCooldown"))
        if cooldown is not None and cooldown <= save_time:
            version = Mengine.getCurrentAccountSetting("EnergyRechargeVersion")
            if version != ENERGY_RECHARGE_VERSION:
                # Old saves could still contain the tick they had already credited.
                cooldown = None

        SystemEnergy.in_infinity_mode = SystemEnergy.isAccountEnergyInfinity() is True
        if self.in_infinity_mode is True:
            energy = max(energy, self.getMaxEnergy())
        elif energy < self.getMaxEnergy():
            cooldown = self.__getRechargeCooldown(energy, cooldown, save_time)
            if timestamp < save_time:
                cooldown = timestamp + max(0, cooldown - save_time)
            else:
                gained, cooldown = self.__getRechargeTicks(energy, cooldown, timestamp)
                energy += gained

        self.__applyProgress(energy, cooldown, timestamp, save=self.in_infinity_mode is False)
        self._loadPaidEnigmas()

    def __initSaveProgress(self):
        def __addExtraAccountSettings(accountID, isGlobal):
            if isGlobal is True:
                return
            Mengine.addCurrentAccountSetting("EnergyPaidEnigmas", u'', None)
            Mengine.addCurrentAccountSetting("Energy", u'', None)
            Mengine.addCurrentAccountSetting("EnergyCooldown", u'', None)
            Mengine.addCurrentAccountSetting("EnergyLastSave", u'', None)
            Mengine.addCurrentAccountSetting("EnergyRechargeVersion", u'', None)
            Mengine.addCurrentAccountSetting("EnergyInfinity", u'', None)

        from Foundation.AccountManager import AccountManager
        AccountManager.addCreateAccountExtra(__addExtraAccountSettings)

    def _onSave(self):
        if Mengine.hasTouchpad() is False or self.isEnable() is False:
            return {}

        self.__saveProgress(self._getTimestamp())
        return {}

    def _onLoad(self, save_dict):
        if Mengine.hasTouchpad() is False or self.isEnable() is False:
            return

        self.__loadProgress()

    def _getTimestamp(self):
        # returns local timestamp from device
        return Mengine.getTime()

    # --- DevToDebug & Cheats ------------------------------------------------------------------------------------------

    def debugCheats(self):
        if _DEVELOPMENT is False:
            return
        if Mengine.getConfigBool("Energy", "EnableDebugCheats", False) is False:
            return

        def _checkEditBox():
            if SystemManager.hasSystem("SystemEditBox"):
                system_edit_box = SystemManager.getSystem("SystemEditBox")
                if system_edit_box.hasActiveEditbox():
                    return False
            return True

        def _cheat(fn, *args):
            if _checkEditBox() is False:
                return
            fn(*args)

        increase_key = Keys.getVirtualKeyCode(Mengine.getConfigString("Energy", "DebugIncreaseKey", "VK_1"))
        increase_value = Mengine.getConfigInt("Energy", "DebugIncreaseValue", 6)
        decrease_key = Keys.getVirtualKeyCode(Mengine.getConfigString("Energy", "DebugDecreaseKey", "VK_2"))
        decrease_value = Mengine.getConfigInt("Energy", "DebugDecreaseValue", 12)

        with self.createTaskChain("EnergyCheat", Repeat=True) as tc:
            with tc.addRaceTask(2) as (tc_increase, tc_decrease):
                tc_increase.addTask("TaskKeyPress", Keys=[increase_key])
                tc_increase.addFunction(_cheat, self.addEnergy, increase_value)

                tc_decrease.addTask("TaskKeyPress", Keys=[decrease_key])
                tc_decrease.addFunction(_cheat, self.withdrawEnergy, decrease_value)

    def __addDevToDebug(self):
        if Mengine.isAvailablePlugin("DevToDebug") is False:
            return
        if Mengine.hasDevToDebugTab("Energy") is True:
            return

        tab = Mengine.addDevToDebugTab("Energy")

        def _title():
            title = "## Energy"
            title += "\n* current energy: `{}`/`{}`".format(self.current_energy, self.getMaxEnergy())
            if self.in_recharging:
                title += "\n* cooldown timestamp: `{}`".format(self.cooldown_timestamp)
                title += "\n* left seconds to 1 refill: `{}`".format(max(0, self.cooldown_timestamp - self._getTimestamp()))
                title += "\n* full refill timestamp: `{}`".format(self.__getRefillEnd(self.current_energy, self.cooldown_timestamp))
            title += "\n* recharging mode = `{}`".format(self.in_recharging)
            title += "\n* free mode = `{}`".format(self.in_free_mode)
            return title

        w_title = Mengine.createDevToDebugWidgetText("title")
        w_title.setText(_title)
        tab.addWidget(w_title)

        # command lines

        def _addEnergy(text):
            energy = int(text)
            self.addEnergy(energy)

        w_add = Mengine.createDevToDebugWidgetCommandLine("add_energy")
        w_add.setTitle("Add energy")
        w_add.setPlaceholder("Input here positive integer")
        w_add.setCommandEvent(_addEnergy)
        tab.addWidget(w_add)

        def _withdrawEnergy(text):
            energy = int(text)
            self.withdrawEnergy(energy)

        w_withdraw = Mengine.createDevToDebugWidgetCommandLine("withdraw_energy")
        w_withdraw.setTitle("Withdraw energy")
        w_withdraw.setPlaceholder("Input here positive integer")
        w_withdraw.setCommandEvent(_withdrawEnergy)
        tab.addWidget(w_withdraw)

        def _setEnergy(text):
            energy = int(text)
            self.setEnergy(energy)

        w_set = Mengine.createDevToDebugWidgetCommandLine("set_energy")
        w_set.setTitle("Set energy")
        w_set.setPlaceholder("Input here positive integer")
        w_set.setCommandEvent(_setEnergy)
        tab.addWidget(w_set)

        def _settingsText():
            title = "**Settings**"
            title += "".join(["\n* {}: `{}`".format(action, state) for action, state in self.s_settings.iteritems()])
            return title

        w_settings_descr = Mengine.createDevToDebugWidgetText("settings_descr")
        w_settings_descr.setText(_settingsText)
        tab.addWidget(w_settings_descr)

        def _updateSettings(text):
            params = text.split(" ")
            if len(params) != 2:
                return

            setting = params[0]
            if setting not in self.s_settings:
                Trace.msg_err("!!! [DevDebugger Energy] setting {!r} not found: {}".format(setting, self.s_settings.keys()))
                return

            if setting in RECHARGE_TIMING_KEYS:
                self._cbGetRemoteConfig("energy_" + setting, params[1])
                return

            value = int(params[1]) if params[1].isdigit() else params[1]
            _Log("!!! changed setting {!r} from {!r} to {!r}".format(setting, self.s_settings[setting], value))
            SystemEnergy.s_settings[setting] = value

        w_settings = Mengine.createDevToDebugWidgetCommandLine("change_settings")
        w_settings.setTitle("Change settings (from list above)")
        w_settings.setPlaceholder("Syntax: <setting name> <new value>")
        w_settings.setCommandEvent(_updateSettings)
        tab.addWidget(w_settings)

        def _actionsText():
            title = "**Actions**"
            title += "".join(["\n* {}: `{}`".format(action, state) for action, state in self.s_actions.iteritems()])
            return title

        w_action_descr = Mengine.createDevToDebugWidgetText("action_descr")
        w_action_descr.setText(_actionsText)
        tab.addWidget(w_action_descr)

        def _updateAction(text):
            action = text
            if action not in self.s_actions:
                Trace.msg_err("!!! [DevDebugger Energy] action {!r} not found: {}".format(action, self.s_actions.keys()))
                return

            value = not self.s_actions[action]
            _Log("!!! changed action {!r} from {!r} to {!r}".format(action, self.s_actions[action], value))
            SystemEnergy.s_actions[action] = value

        w_action = Mengine.createDevToDebugWidgetCommandLine("toggle_action")
        w_action.setTitle("Toggle enable action (from list above)")
        w_action.setPlaceholder("Syntax: <action>")
        w_action.setCommandEvent(_updateAction)
        tab.addWidget(w_action)

        # buttons

        def _toggleFreeMode():
            state = not SystemEnergy.isFreeMode()
            SystemEnergy.setFreeMode(state)

        w_free = Mengine.createDevToDebugWidgetButton("toggle_free_mode")
        w_free.setTitle("Toggle free energy mode")
        w_free.setClickEvent(_toggleFreeMode)
        tab.addWidget(w_free)

    def __remDevToDebug(self):
        if Mengine.isAvailablePlugin("DevToDebug") is False:
            return

        if Mengine.hasDevToDebugTab("Energy") is True:
            Mengine.removeDevToDebugTab("Energy")
