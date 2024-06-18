from Foundation.Systems.SystemMonetization import SystemMonetization as SystemMonetizationBase
from Foundation.MonetizationManager import MonetizationManager
from Foundation.TaskManager import TaskManager
from Foundation.DemonManager import DemonManager
from Foundation.PolicyManager import PolicyManager
from Foundation.SceneManager import SceneManager
from Foundation.Utils import SimpleLogger
from HOPA.ItemManager import ItemManager


_Log = SimpleLogger("SystemMonetization")


class SystemMonetization(SystemMonetizationBase):

    @classmethod
    def _getPossibleRewards(cls):
        rewards = SystemMonetizationBase._getPossibleRewards()
        rewards["Chapter"] = cls.unlockChapter
        rewards["ForceChapter"] = cls.forceUnlockChapter
        return rewards

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
        self.addObserver(Notificator.onRequestPromoCodeResult, self._onGiftExchangeRequestResult)
        self.addObserver(Notificator.onGiftExchangeRedeemResult, self._onGiftExchangeRedeemResult)

        self.addObserver(Notificator.onGameStoreNotEnoughGold, self._onGameStoreNotEnoughGold)
        self.addObserver(Notificator.onEnergyNotEnough, self._onEnergyNotEnough)

        # Gold Balance updater
        self.addObserver(Notificator.onLayerGroupEnable, self._cbLayerGroupEnable)

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

    @classmethod
    def unlockChapter(cls, chapter_id):
        Notification.notify(Notificator.onChapterSelectionBlock, chapter_id, False)
        _Log("unlock chapter '{}'".format(chapter_id))

        if MonetizationManager.getGeneralSetting("CompleteProductsOnChapterUnlock", True) is False:
            return

        for product in MonetizationManager.getProductsInfo().values():
            reward_chapter_id = product.reward.get("Chapter")
            if reward_chapter_id != chapter_id:
                continue
            if SystemMonetization.isProductPurchased(product.id) is False:
                SystemMonetization.addStorageListValue("purchased", product.id)
                _Log("autosave product {!r} - chapter {!r} is already unlocked!".format(
                    product.id, chapter_id), optional=True)

    @classmethod
    def forceUnlockChapter(cls, chapter_id):
        cls.unlockChapter(chapter_id)
        Notification.notify(Notificator.onChapterOpen, chapter_id)

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
