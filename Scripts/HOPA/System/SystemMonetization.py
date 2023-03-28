from Foundation.Systems.SystemMonetization import SystemMonetization as SystemMonetizationBase
from Foundation.MonetizationManager import MonetizationManager
from Foundation.TaskManager import TaskManager
from Foundation.DemonManager import DemonManager
from Foundation.PolicyManager import PolicyManager
from Foundation.Utils import SimpleLogger


_Log = SimpleLogger("SystemMonetization")


class SystemMonetization(SystemMonetizationBase):

    # ==== Policies ====================================================================================================

    def _setupPolicies(self):
        self.__setupNotEnoughResPolicy()

    def __setupNotEnoughResPolicy(self):
        param_key = "NotEnoughMessageProvider"
        default_provider = "MessageOK"
        allowed_providers = {
            default_provider: self.__setupNotEnoughResMessagePolicy,
            "DialogWindow": self.__setupNotEnoughResDialogPolicy,
        }

        message_provider = MonetizationManager.getGeneralSetting(param_key, default_provider)

        if message_provider not in allowed_providers:
            Trace.log("System", 0, "{} '{}' not found, should be: {}".format(
                param_key, message_provider, allowed_providers.keys()))
            message_provider = default_provider

        setuper = allowed_providers[message_provider]
        if setuper() is False:
            default_setuper = allowed_providers[default_provider]
            default_setuper()

    def __setupNotEnoughResMessagePolicy(self):
        PolicyManager.setPolicy("NotEnoughGoldMessage", "PolicyNotEnoughGoldMessage")
        PolicyManager.setPolicy("NotEnoughEnergyMessage", "PolicyNotEnoughEnergyMessage")
        return True

    def __setupNotEnoughResDialogPolicy(self):
        if DemonManager.hasDemon("DialogWindow") is False:
            Trace.log("System", 0, "NotEnoughGold policy can't be with DialogWindow - it's not active")
            return False

        PolicyManager.setPolicy("NotEnoughGoldMessage", "PolicyNotEnoughGoldDialog")
        PolicyManager.setPolicy("NotEnoughEnergyMessage", "PolicyNotEnoughEnergyDialog")
        return True

    # ==== Observers ===================================================================================================

    def _setupObservers(self):
        # GameStore
        self.addObserver(Notificator.onGiftExchangeRedeemResult, self._onGiftExchangeRedeemResult)
        self.addObserver(Notificator.onGameStoreNotEnoughGold, self._onGameStoreNotEnoughGold)
        self.addObserver(Notificator.onEnergyNotEnough, self._onEnergyNotEnough)

        # Gold Balance updater
        self.addObserver(Notificator.onLayerGroupEnable, self._cbLayerGroupEnable)

    def _onGameStoreNotEnoughGold(self, gold, descr):
        NotEnoughMoneyPageID = MonetizationManager.getGeneralSetting("NotEnoughMoneyPageID")

        TaskManager.runAlias("AliasNotEnoughGold", None, Gold=gold, Descr=descr, PageID=NotEnoughMoneyPageID)
        return False

    def _onEnergyNotEnough(self, action_name):
        NotEnoughMoneyPageID = MonetizationManager.getGeneralSetting("NotEnoughMoneyPageID")

        TaskManager.runAlias("AliasNotEnoughEnergy", None, Action=action_name, PageID=NotEnoughMoneyPageID)
        return False

    @staticmethod
    def _onGiftExchangeRedeemResult(reward_type, reward_amount):    # todo
        _Log("onGiftExchangeRedeemResult DUMMY - {} {}".format(reward_type, reward_amount))
        return False

    def _cbLayerGroupEnable(self, group_name):
        if group_name in ["BalanceIndicator", SystemMonetization.game_store_name]:
            Notification.notify(Notificator.onUpdateGoldBalance, str(self.getBalance()))
        return False
