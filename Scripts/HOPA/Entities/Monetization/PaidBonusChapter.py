from Foundation.DemonManager import DemonManager
from Foundation.MonetizationManager import MonetizationManager
from Foundation.Systems.SystemMonetization import SystemMonetization
from Foundation.TaskManager import TaskManager
from HOPA.Entities.Monetization.BaseComponent import BaseComponent


TC_NAME = "PaidBonusChapter"


class PaidBonusChapter(BaseComponent):
    _settings = {
        "is_enable": "EnablePaidBonusChapter",
        "product_id": "BonusChapterProductID",
        "movie": "PaidBonusChapterMovie",
        "alias_id": "PaidBonusChapterAliasID",
        "text_id": "PaidBonusChapterTextID",
        "extra_text_id": "ExtraPaidBonusChapterTextID",
    }
    _defaults = {
        "product_id": "tech_chapter",
        "movie": "Movie2Button_BuyChapter",
        "group": "ChapterSelection",
        "alias_id": "$AliasBuyChapter",
        "text_id": "ID_TEXT_BUY_CHAPTER_0",
    }

    def _createParams(self):
        self.demon_name = self.group_name
        self.demon = DemonManager.getDemon(self.demon_name) if DemonManager.hasDemon(self.demon_name) else None
        self.extra_text_id = self._getMonetizationParam("extra_text_id")

    def _check(self):
        if self.product is None:
            self._error("Not found product {!r}".format(self._product_lookup_id))
            return False
        if self.demon is None:
            self._error("Not found demon {!r}".format(self.demon_name))
            return False
        if self.demon.hasObject(self.movie_name) is False:
            self._error("Not found movie {!r} in demon {!r}".format(self.movie_name, self.demon_name))
            return False
        return True

    def _initialize(self):
        self.button = self.demon.getObject(self.movie_name)
        return True

    def _run(self):
        self.addObserver(Notificator.onSelectAccount, self._cbSelectAccount)
        self._prepareText()
        return True

    def _prepareText(self):
        params = {"": self.text_id, "extra": self.extra_text_id}
        is_delayed = SystemMonetization.isPurchaseDelayed(self.product.id)

        for env, text_id in params.items():
            if text_id is None:
                continue

            if is_delayed is True:
                self._setDelayedText(env, text_id)
                continue

            Mengine.setTextAlias(env, self.alias_id, text_id)

            # prepare price every open ChapterSelection (price could change during the game)
            if "%s" in Mengine.getTextFromID(text_id):
                self.addObserver(Notificator.onLayerGroupEnableBegin, self._cbPreparePrice, env, text_id)

    def _setDelayedText(self, env, text_id):
        if text_id == self.text_id:
            Mengine.setTextAlias(env, self.alias_id, "ID_TEXT_RESTORE_PURCHASES")
        elif text_id == self.extra_text_id:
            Mengine.setTextAlias(env, self.alias_id, "ID_EMPTY_TEXT")

    def _cbSelectAccount(self, account_id):
        if TaskManager.existTaskChain(TC_NAME):
            TaskManager.cancelTaskChain(TC_NAME)

        if SystemMonetization.isProductPurchased(self.product.id) is True:
            self.button.setEnable(False)
            return False

        # enable block button and block chapter even if player complete main chapter
        self.button.setEnable(True)
        Notification.notify(Notificator.onChapterSelectionBlock, "Bonus", True)

        with TaskManager.createTaskChain(Name=TC_NAME) as tc:
            with tc.addRepeatTask() as (repeat, until):
                repeat.addTask("TaskMovie2ButtonClick", Movie2Button=self.button)
                with repeat.addIfTask(SystemMonetization.isPurchaseDelayed, self.product.id) as (delayed, default):
                    delayed.addNotify(Notificator.onReleasePurchased, self.product.id)
                    default.addScope(SystemMonetization.scopePay, prod_id=self.product.id)

                until.addListener(Notificator.onPaySuccess, Filter=lambda prod_id: prod_id == self.product.id)

            # unblock chapter and remove purchase button
            tc.addNotify(Notificator.onChapterSelectionBlock, "Bonus", False)
            tc.addDisable(self.button)

        return False

    def _cbPreparePrice(self, group_name, env, text_id):
        if group_name != self.group_name:
            return False

        if SystemMonetization.isProductPurchased(self.product.id) is True:
            return True     # stop observer

        if SystemMonetization.isPurchaseDelayed(self.product.id) is True:
            self._setDelayedText(env, text_id)
            return True

        currency = MonetizationManager.getCurrentCurrencySymbol() or ""
        price_format = "{price} {currency}".format(price=self.product.price, currency=currency)

        Mengine.setTextAlias(env, self.alias_id, text_id)
        Mengine.setTextAliasArguments(env, self.alias_id, price_format)

        return False

    def _cleanUp(self):
        if TaskManager.existTaskChain(TC_NAME):
            TaskManager.cancelTaskChain(TC_NAME)
