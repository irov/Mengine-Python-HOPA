from Foundation.DemonManager import DemonManager
from Foundation.MonetizationManager import MonetizationManager
from Foundation.PolicyManager import PolicyManager
from Foundation.SystemManager import SystemManager
from HOPA.Entities.Monetization.BaseComponent import BaseComponent
from HOPA.Entities.Monetization.Coin import Coin
from HOPA.System.SystemTutorialFade import SystemTutorialFade


class Hint(BaseComponent):
    component_id = "Hint"
    _settings = {
        "is_enable": "EnablePaidHint",
        "product_id": "HintProductID",
        "alias_id": "AliasCoinUsePrice",
        "text_id": "HintPriceTextID",
        "movie": "CoinMovie2Name",
    }
    _defaults = {
        "product_id": "tech_hint",
        "alias_id": "$AliasCoinUsePrice",
        "text_id": "ID_TEXT_MONETIZE_NEGATIVE_PRICE",
        "movie": "Movie2_Coin",
        "group": "Hint"
    }

    def _createParams(self):
        Hint = DemonManager.getDemon(self.group_name)
        self.demon = Hint
        self.rollback_actions = {
            Hint.ACTION_EMPTY_USE: MonetizationManager.getGeneralSetting("HintRollbackIfDummy", True),
            Hint.ACTION_REGULAR_USE: False,
            Hint.ACTION_MIND_USE: MonetizationManager.getGeneralSetting("HintRollbackIfMind", True),
            Hint.ACTION_NO_RELOAD_USE: MonetizationManager.getGeneralSetting("HintRollbackIfNoReload", False)
        }

        self.coin = Coin(self)

    def _check(self):
        if self.product is None:
            self._error("Not found product {!r}".format(self._product_lookup_id))
            return False
        if self.coin.initialize() is False:
            return False
        return True

    def _initialize(self):
        self.text_args = [self.product.price]
        return True

    def _run(self):
        PolicyManager.setPolicy("HintPlay", "PolicyHintPlayPaid")
        self.addObserver(Notificator.onHintClick, self._cbHintClick)

    def getProductPrice(self):
        if SystemTutorialFade.is_working is True:
            return 0
        return super(Hint, self).getProductPrice()

    def _cleanUp(self):
        self.coin.cleanUp()

    def scopeActivate(self, source, default_task_name):
        if self.demon.isActive() is False:
            self._error("Demon {!r} is not active".format(self.demon.getName()))
            source.addTask(default_task_name)
            return

        hint = self.demon.entity

        currency = self.getProductCurrency()
        if currency == "Gold":
            source.addScope(self._system.scopePayGold, descr=self.component_id, scopeSuccess=hint.scopeHintLogic)

        elif currency == "Energy":
            def _filterEnergy(action_name, *_):
                return action_name == self.component_id

            price = self.getProductPrice()
            SystemEnergy = SystemManager.getSystem("SystemEnergy")

            with source.addParallelTask(2) as (tc_response, tc_request):
                with tc_response.addRaceTask(2) as (tc_pay_ok, tc_pay_fail):
                    tc_pay_ok.addListener(Notificator.onEnergyConsumed, Filter=_filterEnergy)
                    tc_pay_ok.addScope(hint.scopeHintLogic)
                    tc_pay_fail.addListener(Notificator.onEnergyNotEnough, Filter=_filterEnergy)
                tc_request.addFunction(SystemEnergy.payEnergy, price, self.component_id)

    # observers

    def _cbHintClick(self, hint_object, valid, action_id):
        should_rollback = self.rollback_actions[action_id]
        if should_rollback is False:
            return False
        if SystemTutorialFade.is_working is True:
            return False

        self._system.rollbackCurrency(component_tag=self.component_id)
        return False
