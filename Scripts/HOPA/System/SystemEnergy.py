from Event import Event
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

EVENT_CHANGED_BALANCE = Event("onEnergyBalanceChanged")
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


class SystemEnergy(System):
    s_settings = {}  # key-value energy params
    s_actions = {}  # { action_name: true/false } - is action enable
    s_actions_price = {}  # { action_name: int price } - how many energy would be withdrawn

    in_recharging = False
    in_free_mode = False        # consume method always return True if free mode is True
    in_infinity_mode = False    # free mode, but shows it for user

    s_paid_enigmas = SecureStringValue("EnergyPaidEnigmas", "")

    def __init__(self):
        super(SystemEnergy, self).__init__()
        self.current_energy = None
        self.end_refill_timestamp = None  # timestamp when energy will be fully restored
        self.cooldown_timestamp = None  # timestamp when one unit of energy will be restored
        self.__cooldown_left_seconds = None  # for DevToDebug view
        self.timer = None
        self._balance_change_observer = None

    @staticmethod
    def isEnable():
        return SystemEnergy.s_settings.get("enable", False)

    def _onInitialize(self):
        if Mengine.getConfigBool("Energy", "Enable", False) is False:
            return

        settings = {
            "enable": True,
            "max_energy": Mengine.getConfigInt("Energy", "MaxEnergy", 300),
            "default_energy_consumption": Mengine.getConfigInt("Energy", "DefaultConsumption", 6),
            "refill_per_time": Mengine.getConfigInt("Energy", "RefillEnergyPerTime", 1),
            "refill_time": Mengine.getConfigFloat("Energy", "RefillTime", 240.0),
        }

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
        self._balance_change_observer = EVENT_CHANGED_BALANCE.addObserver(self._cbBalanceChange)
        if self.s_actions["EnterHOG"] is True:
            self.addObserver(Notificator.onSceneActivate, self._cbSceneActivate)
            self.addObserver(Notificator.onSceneDeactivate, self._cbSceneDeactivate)

    def _cbGetRemoteConfig(self, key, value):
        """ Observer that patch energy config - key should have 'energy_' prefix.
            You can't patch values from `ignore_list`.
            All values come as string, but will be cast to same type as old value.
        """
        if key.startswith("energy_") is False:
            return False
        _key = key[len("energy_"):]

        ignore_list = ["enable"]
        if _key in ignore_list:
            return False

        def _tryPatch(patch_dict, patch_key, val):
            cast = type(patch_dict[patch_key])
            try:
                patch_dict[patch_key] = cast(val)
            except ValueError:
                Trace.msg_err("SystemEnergy can't patch {!r}: wrong type, must be {}".format(patch_key, cast))

        for possible_dict in [SystemEnergy.s_settings, SystemEnergy.s_actions_price]:
            if _key in possible_dict:
                _tryPatch(possible_dict, _key, value)

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
        if self._balance_change_observer is not None:
            EVENT_CHANGED_BALANCE.removeObserver(self._balance_change_observer)
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
                tc.addFunction(TransitionManager.changeScene, prev_game_scene_name)
                tc.addListener(Notificator.onSceneInit, Filter=lambda scene_name: scene_name == prev_game_scene_name)
                tc.addNotify(Notificator.onEnergyNotEnough, action_name, action_value)

            _Log("Not enough energy to play this game - transit to prev scene :(")

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

    def setInfinityMode(self, state):
        SystemEnergy.in_infinity_mode = state
        self.notifyUpdateBalance()
        if state is True:
            self.onCharged()
        Mengine.changeCurrentAccountSettingBool("EnergyInfinity", state)
        Mengine.saveAccounts()

    @staticmethod
    def isFreeMode():
        return SystemEnergy.in_free_mode is True or SystemEnergy.in_infinity_mode is True

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

    def balanceChanger(action):  # noqa
        def decorate(bound_method):
            def wrap(self, energy):
                last_energy = self.current_energy
                bound_method(self, energy)
                _Log("{} {}: {}".format(action, energy, self.current_energy))
                EVENT_CHANGED_BALANCE(last_energy, self.current_energy)
                return False
            return wrap
        return decorate

    @balanceChanger("withdraw")  # noqa
    def withdrawEnergy(self, energy):
        if self.current_energy - energy < 0:
            self.current_energy = 0
        else:
            self.current_energy -= energy
        return False

    @balanceChanger("add")  # noqa
    def addEnergy(self, energy):
        self.current_energy += energy
        return False

    @balanceChanger("set")  # noqa
    def setEnergy(self, energy):
        if energy == ENERGY_INFINITY_CODE:
            self.setInfinityMode(True)
            return False
        self.current_energy = 0 if energy < 0 else energy
        return False

    def consume(self, action_name, notify_not_enough_energy=True):
        """ Used for paid actions that depends on own system energy.
            Checks free mode, so user can not pay energy if it is enabled.

            :returns: `True` if payment success (or was free mode), `False` if not enough energy.
        """
        if SystemEnergy.isFreeMode() is True:
            return True

        action_value = self.getActionEnergy(action_name)
        return self.payEnergy(action_value, action_name, notify_not_enough_energy)

    def payEnergy(self, amount, action_name, notify_not_enough_energy=True):
        """ Performs actual payment with energy. [!] Ignores free mode.

            :returns: `True` if payment success, `False` if not enough energy.
        """
        if self.isEnoughEnergy(amount) is False:
            if notify_not_enough_energy is True:
                Notification.notify(Notificator.onEnergyNotEnough, action_name, amount)
            return False

        self.withdrawEnergy(amount)
        Notification.notify(Notificator.onEnergyConsumed, action_name, amount)
        return True

    # reactions on balance change, handle recharge timer:

    def _cbBalanceChange(self, prev_balance, new_balance):
        if prev_balance == new_balance:
            return

        self.notifyUpdateBalance()

        max_energy = self.getMaxEnergy()

        if self.current_energy < max_energy:
            if prev_balance <= new_balance:
                # energy increased
                self.__saveProgress()
                return

            rest_energy = max_energy - self.current_energy
            seconds_to_refill = rest_energy * self.s_settings["refill_time"]

            if self.end_refill_timestamp is None:
                time = self._getTimestamp()
                end_refill_timestamp = time + seconds_to_refill
                self.end_refill_timestamp = end_refill_timestamp
                self.startRecharge(time)
            else:
                self.end_refill_timestamp += seconds_to_refill

        else:  # current_energy >= max_energy
            self.onCharged()

        self.__saveProgress()

    def notifyUpdateBalance(self):
        if self.in_infinity_mode is True:
            Notification.notify(Notificator.onUpdateEnergyBalance, ENERGY_INFINITY_CODE)
            return
        Notification.notify(Notificator.onUpdateEnergyBalance, self.current_energy)

    # === Refill =======================================================================================================

    def refillEnergy(self, energy):
        max_energy = self.getMaxEnergy()
        if self.current_energy + energy > max_energy:
            self.setEnergy(max_energy)
        else:
            Notification.notify(Notificator.onEnergyIncrease, energy)

    def startRecharge(self, start_time=None):
        """ Starts recharge
            (set end_refill_timestamp before call)
        """
        if self.end_refill_timestamp is None:
            Trace.log("System", 0, "can't startRecharge: end_refill_timestamp is None (init it before call)")
            return

        time = start_time or self._getTimestamp()

        if self.cooldown_timestamp is None or (self.cooldown_timestamp - time) < 0:
            # if no recharge or cooldown_timestamp is too old - reload it
            self.reloadCooldown(start_time)

        self.setTimer()
        SystemEnergy.in_recharging = True
        Notification.notify(Notificator.onEnergyRecharge)

        _Log("start recharge [{}] - end at {} ({} seconds left)".format(
            start_time, self.end_refill_timestamp, self.end_refill_timestamp - start_time))

    def onCharged(self):
        """ Called when energy is fully recharged """

        self.removeTimer()
        SystemEnergy.in_recharging = False
        Notification.notify(Notificator.onEnergyCharged)
        self.end_refill_timestamp = None
        self.cooldown_timestamp = None

        _Log("charge done")

    def setTimer(self):
        if self.timer is not None:
            Mengine.removeChronometer(self.timer)
        self.timer = Mengine.addChronometer(self._onTimer)

    def _onTimer(self, time):
        if self.cooldown_timestamp is None or self.end_refill_timestamp is None:
            Trace.log("System", 0, "SystemEnergy start timer, but cooldown_timestamp [{}] or end_refill_timestamp [{}] is None".format(
                self.cooldown_timestamp, self.end_refill_timestamp))
            self.onCharged()
            return

        timestamp = Mengine.getTime()

        one_time_left = self.cooldown_timestamp - timestamp  # for 1 charge
        self.__cooldown_left_seconds = one_time_left

        _Log("    left: {}s  ({} - {})".format(one_time_left, self.cooldown_timestamp, timestamp), optional=True)

        if one_time_left <= 0:
            energy_per_time = self.s_settings["refill_per_time"]
            self.refillEnergy(energy_per_time)
            if self.end_refill_timestamp is not None:
                self.reloadCooldown(timestamp)
            self.__cooldown_left_seconds = None

        _, hours, minutes, seconds = calcTime(one_time_left)
        EVENT_UPDATE_TIMER(hours, minutes, seconds)

    def removeTimer(self):
        if self.timer is None:
            return
        Mengine.removeChronometer(self.timer)
        self.timer = None

    def getCooldownTimestamp(self, start_time=None):
        if self.end_refill_timestamp is None:
            return None

        time = start_time or self._getTimestamp()
        left_seconds = self.end_refill_timestamp - time

        if left_seconds <= 0:
            return None

        device_time = Mengine.getTime()     # we use device time because timer works with it
        if (left_seconds // self.s_settings["refill_time"]) == 0:
            cooldown = device_time + left_seconds
        else:
            cooldown = device_time + self.s_settings["refill_time"]

        return cooldown

    def reloadCooldown(self, start_time=None):
        self.cooldown_timestamp = self.getCooldownTimestamp(start_time)
        if self.cooldown_timestamp is not None:
            self.cooldown_timestamp += 1  # fix 1s lose

    # === Save\Load ====================================================================================================

    def __saveProgress(self):
        Mengine.changeCurrentAccountSetting("Energy", unicode(self.current_energy))
        Mengine.changeCurrentAccountSetting("EnergyRefill", unicode(self.end_refill_timestamp))
        Mengine.changeCurrentAccountSetting("EnergyCooldown", unicode(self.cooldown_timestamp))
        Mengine.changeCurrentAccountSetting("EnergyLastSave", unicode(self._getTimestamp()))

        Mengine.saveAccounts()

    def __loadProgress(self):
        params = {
            # key: [save_key, default_value, cast_type]
            "current_energy": ["Energy", self.getMaxEnergy(), int],
            "end_refill_timestamp": ["EnergyRefill", None, float],
            "cooldown_timestamp": ["EnergyCooldown", None, float]
        }

        for atr, (save_key, default_value, cast) in params.items():
            save = Mengine.getCurrentAccountSetting(save_key)
            if save == "":
                self.__dict__[atr] = default_value
            elif save == "None":
                self.__dict__[atr] = None
            else:
                try:
                    self.__dict__[atr] = cast(save)
                except ValueError as e:
                    if _DEVELOPMENT is True:
                        Trace.log("System", 0, "Can't load save {}={}: {}. Set to default value".format(atr, save, e))
                    self.__dict__[atr] = default_value
        try:
            save_time = int(Mengine.getCurrentAccountSetting("EnergyLastSave"))
        except ValueError:
            save_time = self._getTimestamp()

        if isinstance(self.current_energy, int) is False:
            Trace.log("System", 0, "SystemEnergy._onLoad current_energy is not integer: {} {}".format(self.current_energy, type(self.current_energy)))
            self._setupInitialCurrentEnergy()

        if Mengine.getCurrentAccountSettingBool("EnergyInfinity") is True:
            SystemEnergy.in_infinity_mode = True
            self.current_energy = max(self.current_energy, self.getMaxEnergy())
        else:
            self.chargeOnLoad(save_time)

        self._loadPaidEnigmas()

    def __initSaveProgress(self):
        def __addExtraAccountSettings(accountID, isGlobal):
            if isGlobal is True:
                return
            Mengine.addCurrentAccountSetting("EnergyPaidEnigmas", u'', None)
            Mengine.addCurrentAccountSetting("Energy", u'', None)
            Mengine.addCurrentAccountSetting("EnergyRefill", u'', None)
            Mengine.addCurrentAccountSetting("EnergyCooldown", u'', None)
            Mengine.addCurrentAccountSetting("EnergyLastSave", u'', None)
            Mengine.addCurrentAccountSetting("EnergyInfinity", u'', None)

        from Foundation.AccountManager import AccountManager
        AccountManager.addCreateAccountExtra(__addExtraAccountSettings)

    def _onSave(self):
        if Mengine.hasTouchpad() is False or self.isEnable() is False:
            return {}

        self.__saveProgress()
        return {}

    def _onLoad(self, save_dict):
        if Mengine.hasTouchpad() is False or self.isEnable() is False:
            return

        self.__loadProgress()

    def chargeOnLoad(self, save_time):
        time = self._getTimestamp()
        time_passed = time - save_time
        refill_time = self.s_settings["refill_time"]
        energy_accumulated = int(time_passed // refill_time)
        max_energy = self.getMaxEnergy()

        if self.current_energy >= max_energy:
            # User has enough energy, can't accumulate more
            energy_accumulated = 0
        elif (self.current_energy + energy_accumulated) > max_energy:
            # User hasn't enough energy, adjust accumulated (energy bigger than maximum)
            energy_accumulated = max_energy - self.current_energy

        # CASE 1: no charging process
        # CASE 2: full charge complete
        if self.end_refill_timestamp is None or self.end_refill_timestamp - time <= 0:
            if self.current_energy < max_energy:
                self.setEnergy(max_energy)
            self.onCharged()
        # CASE 3: accumulate some energy, but charging in progress
        else:
            if time < save_time:
                _Log("cheater cheater cheater cheater cheater", err=True)
                self.setEnergy(0)
            else:
                self.addEnergy(energy_accumulated)
            if self.end_refill_timestamp is not None:
                # if we add some energy, but it is not enough
                self.startRecharge(time)

        self.__saveProgress()
        _Log("{} seconds have passed since the last game: {} energy accumulated"
             .format(time_passed, energy_accumulated), optional=True)

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
                title += "\n* left seconds to 1 refill: `{}`".format(self.__cooldown_left_seconds)
                title += "\n* full refill timestamp: `{}`".format(self.end_refill_timestamp)
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
            title += "".join(["\n* {}: `{}`".format(action, state) for action, state in self.s_settings.items()])
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
            title += "".join(["\n* {}: `{}`".format(action, state) for action, state in self.s_actions.items()])
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
