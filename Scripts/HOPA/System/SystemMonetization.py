from Foundation.Systems.SystemMonetization import SystemMonetization as SystemMonetizationBase
from Foundation.MonetizationManager import MonetizationManager
from Foundation.SecureStringValue import SecureStringValue
from Foundation.TaskManager import TaskManager
from Foundation.DemonManager import DemonManager
from Foundation.PolicyManager import PolicyManager
from Foundation.SceneManager import SceneManager
from Foundation.SystemManager import SystemManager
from Foundation.Utils import SimpleLogger
from HOPA.ItemManager import ItemManager


_Log = SimpleLogger("SystemMonetization")


class SystemMonetization(SystemMonetizationBase):

    def _onInitialize(self):
        super(SystemMonetization, self)._onInitialize()

        for key in ("unlockedChapters", "openedChapters", "unlockedScenes"):
            SystemMonetization.addStorageType(key, SecureStringValue, "")

        SystemMonetization.addRewardType("Energy", SystemMonetization._prepareEnergy, SystemMonetization._validAmount,
                                         additive=True, ready=SystemMonetization._isEnergyReady)
        SystemMonetization.addRewardType("EnergyInfinity", SystemMonetization._prepareInfinityEnergy,
                                         SystemMonetization._validEnableFlag, ready=SystemMonetization._isEnergyReady)
        SystemMonetization.addRewardType("Chapter", SystemMonetization._prepareChapter, SystemMonetization._validContentId,
                                         ready=SystemMonetization._isChapterReady,
                                         restore=lambda transaction, value: transaction.addListValue("unlockedChapters", value))
        SystemMonetization.addRewardType("ForceChapter", SystemMonetization._prepareForceChapter, SystemMonetization._validContentId,
                                         ready=SystemMonetization._isChapterReady,
                                         restore=lambda transaction, value: transaction.addListValue("openedChapters", value))
        SystemMonetization.addRewardType("SceneUnlock", SystemMonetization._prepareScene, SystemMonetization._validContentId,
                                         ready=SceneManager.hasScene,
                                         restore=lambda transaction, value: transaction.addListValue("unlockedScenes", value))

    @staticmethod
    def _validContentId(value):
        return isinstance(value, basestring) and len(value) > 0

    # ==== Energy ======================================================================================================

    @staticmethod
    def _getEnergySystem():
        if SystemManager.hasSystem("SystemEnergy") is False:
            return None

        system = SystemManager.getSystem("SystemEnergy")
        if system.isRun() is False or system.isEnable() is False or system.current_energy is None:
            return None

        return system

    @staticmethod
    def _isEnergyReady(value):
        return SystemMonetization._getEnergySystem() is not None

    @staticmethod
    def _prepareEnergy(transaction, value):
        return SystemMonetization._getEnergySystem().preparePurchaseEnergy(transaction, value)

    @staticmethod
    def _prepareInfinityEnergy(transaction, value):
        return SystemMonetization._getEnergySystem().preparePurchaseEnergy(transaction, 0, infinity=True)

    @staticmethod
    def addEnergy(energy):
        return SystemMonetization.sendReward(rew_dict={"Energy": energy})

    @staticmethod
    def setInfinityEnergy(code):
        return SystemMonetization.sendReward(rew_dict={"EnergyInfinity": code})

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
        self.addObserver(Notificator.onPayUnavailable, self._onPayUnavailable)
        self.addObserver(Notificator.onSessionLoadComplete, self._restoreEntitlements)
        self.addObserver(Notificator.onSelectAccount, self._restoreEntitlements)
        self.addObserver(Notificator.onRequestPromoCodeResult, self._onGiftExchangeRequestResult)
        self.addObserver(Notificator.onGiftExchangeRedeemResult, self._onGiftExchangeRedeemResult)

        self.addObserver(Notificator.onGameStoreNotEnoughGold, self._onGameStoreNotEnoughGold)
        self.addObserver(Notificator.onEnergyNotEnough, self._onEnergyNotEnough)

        # Gold Balance updater
        self.addObserver(Notificator.onLayerGroupEnable, self._cbLayerGroupEnable)

    def _onPayUnavailable(self, prod_id, reason):
        text_ids = {
            "storage_error": "ID_TEXT_PURCHASE_STORAGE_ERROR",
            "not_ready": "ID_TEXT_PURCHASE_NOT_READY",
            "unsupported": "ID_TEXT_PURCHASE_UNAVAILABLE",
        }
        text_id = MonetizationManager.getGeneralSetting("PurchaseErrorText_" + reason, text_ids[reason])
        if TaskManager.existTaskChain("MonetizationPurchaseError") is False:
            with TaskManager.createTaskChain(Name="MonetizationPurchaseError") as tc:
                tc.addTask("AliasSystemMessage", TextID=text_id)
        return False

    def _onGameStoreNotEnoughGold(self, gold, descr):
        if descr == "Exchange":
            return False

        NotEnoughMoneyPageID = MonetizationManager.getGeneralSetting("NotEnoughMoneyPageID")

        TaskManager.runAlias("AliasNotEnoughGold", None, Gold=gold, Descr=descr, PageID=NotEnoughMoneyPageID)
        return False

    def _onEnergyNotEnough(self, action_name, amount):
        if action_name == "Exchange":
            return False

        NotEnoughMoneyPageID = MonetizationManager.getGeneralSetting("NotEnoughMoneyPageID")

        TaskManager.runAlias("AliasNotEnoughEnergy", None,
                             Action=action_name, PageID=NotEnoughMoneyPageID, Amount=amount)
        return False

    def _cbLayerGroupEnable(self, group_name):
        if group_name in ["BalanceIndicator", SystemMonetization.game_store_name]:
            Notification.notify(Notificator.onUpdateGoldBalance, str(self.getBalance()))
        return False

    # ==== Chapter block ===============================================================================================

    @staticmethod
    def _isChapterReady(chapter_id):
        if SystemManager.hasSystem("SystemChapterSelection") is False:
            return False

        system = SystemManager.getSystem("SystemChapterSelection")
        return system.isRun() is True and system.getChapterSelection(chapter_id) is not None

    @staticmethod
    def _prepareChapter(transaction, chapter_id):
        transaction.addListValue("unlockedChapters", chapter_id)
        transaction.afterCommit(Notification.notify, Notificator.onChapterSelectionBlock, chapter_id, False)
        return True

    @staticmethod
    def _prepareForceChapter(transaction, chapter_id):
        SystemMonetization._prepareChapter(transaction, chapter_id)
        transaction.addListValue("openedChapters", chapter_id)
        transaction.afterCommit(Notification.notify, Notificator.onChapterOpen, chapter_id)
        return True

    @staticmethod
    def _prepareScene(transaction, scene_id):
        transaction.addListValue("unlockedScenes", scene_id)
        return True

    @staticmethod
    def unlockChapter(chapter_id):
        return SystemMonetization.sendReward(rew_dict={"Chapter": chapter_id})

    @staticmethod
    def forceUnlockChapter(chapter_id):
        return SystemMonetization.sendReward(rew_dict={"ForceChapter": chapter_id})

    def _restoreEntitlements(self, *args):
        if self._isStorageReady() is False:
            return False
        for chapter_id in self.getStorageListValues("unlockedChapters") + self.getStorageListValues("openedChapters"):
            if self._isChapterReady(chapter_id) is True:
                Notification.notify(Notificator.onChapterSelectionBlock, chapter_id, False)
        for chapter_id in self.getStorageListValues("openedChapters"):
            if self._isChapterReady(chapter_id) is True:
                Notification.notify(Notificator.onChapterOpen, chapter_id)
        return False

    # ==== Promo codes =================================================================================================

    def _trySendPromoItem(self, item_promo_id):
        items = ItemManager.getAllItems()
        for item_id, item in items.items():
            if item.promoID is None:
                continue
            if item.promoID == item_promo_id:
                Notification.notify(Notificator.onGiftExchangeRedeemResult, "add_item", item_id)
                return True
        return False

    def _onGiftExchangeRequestResult(self, code):
        if len(code) != 8:
            _Log("onGiftExchangeRequestResult - invalid code length: {!r}".format(code), err=True)
            Notification.notify(Notificator.onGiftExchangeRedeemResult, None, None)
            return False

        prefix = code[:2]
        if prefix == "i_":
            item_promo_id = code[2:]
            if self._trySendPromoItem(item_promo_id) is True:
                # sends (onGiftExchangeRedeemResult, "add_item", item_id) inside
                return False

        unlock_bonus_code = MonetizationManager.getGeneralSetting("GiftExchangePromoCodeUnlockBonus")
        if unlock_bonus_code is not None and code == unlock_bonus_code:
            Notification.notify(Notificator.onGiftExchangeRedeemResult, "force_chapter", None)
            return False

        _Log("onGiftExchangeRequestResult - invalid code: {!r}".format(code), err=True)
        Notification.notify(Notificator.onGiftExchangeRedeemResult, None, None)
        return False

    def _getPossibleGiftExchangeRewards(self, reward_amount):
        rewards = {
            "golds": (self.addGold, reward_amount),
            "energy": (self.addEnergy, reward_amount),
            "chapter": (self.unlockChapter, "Bonus"),
            "force_chapter": (self.forceUnlockChapter, "Bonus"),
        }

        # GUIDES

        def _callPaySuccess(prod_id):
            Notification.notify(Notificator.onPaySuccess, prod_id)

        guide_product_id = MonetizationManager.getGeneralSetting("GuidesProductID")
        if MonetizationManager.hasProductInfo(guide_product_id):
            guide_product = MonetizationManager.getProductInfo(guide_product_id)
            rewards["guide"] = (_callPaySuccess, guide_product.id)

        # ADD_ITEM

        def _addItem(item_id):
            tc_name = "GiftExchange_AddItem_{}".format(item_id)
            if TaskManager.existTaskChain(tc_name) is True:
                return
            with TaskManager.createTaskChain(Name=tc_name) as tc:
                inventory = DemonManager.getDemon("Inventory")
                tc.addListener(Notificator.onSceneActivate, Filter=lambda name: SceneManager.isGameScene(name) is True)
                tc.addTask("AliasInventoryAddInventoryItem", Inventory=inventory, ItemName=item_id)

        rewards["add_item"] = (_addItem, reward_amount)

        return rewards

    def _onGiftExchangeRedeemResult(self, reward_type, reward_amount):
        _Log("onGiftExchangeRedeemResult - {} {}".format(reward_type, reward_amount))

        if reward_type is None:
            return False

        rewards = self._getPossibleGiftExchangeRewards(reward_amount)

        if reward_type not in rewards:
            Trace.log("System", 0, "SystemMonetization reward_type {!r} is unknown".format(reward_type))
            return False

        send_reward, arg = rewards[reward_type]
        send_reward(arg)

        return False
