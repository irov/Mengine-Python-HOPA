from Foundation.PolicyManager import PolicyManager
from Foundation.SceneManager import SceneManager
from Foundation.Systems.SystemMonetization import SystemMonetization
from Foundation.DemonManager import DemonManager
from Foundation.SystemManager import SystemManager
from Foundation.Utils import SimpleLogger
from HOPA.EnigmaManager import EnigmaManager
from HOPA.Entities.Monetization.BaseComponent import BaseComponent
from HOPA.Entities.Monetization.Coin import Coin
from HOPA.System.SystemItemPlusScene import SystemItemPlusScene
from HOPA.System.SystemTutorialFade import SystemTutorialFade


_Log = SimpleLogger("PaidSkipPuzzle", option="monetization")


class SkipPuzzle(BaseComponent):
    component_id = "SkipPuzzle"
    _settings = {
        "is_enable": "EnablePaidSkip",
        "product_id": "SkipProductID",
        "alias_id": "AliasCoinUsePrice",
        "text_id": "SkipPriceTextID",
        "movie": "CoinMovie2Name",
    }
    _defaults = {
        "product_id": "tech_skip",
        "alias_id": "$AliasCoinUsePrice",
        "text_id": "ID_TEXT_MONETIZE_NEGATIVE_PRICE",
        "movie": "Movie2_Coin",
        "group": "SkipPuzzle",
    }

    def _createParams(self):
        SkipPuzzle = DemonManager.getDemon(self.group_name)
        self.demon = SkipPuzzle
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
        self.addObserver(Notificator.onEnigmaPlay, self._skipPurchasedEnigma)  # fast skip mg
        self.addObserver(Notificator.onGameStorePayGoldSuccess, self._cbPayGoldSuccess)
        PolicyManager.setPolicy("SkipPuzzlePlay", "PolicySkipPuzzlePlayPaid")

    def _cbPayGoldSuccess(self, gold, descr):
        if descr != "SkipPuzzle":
            return False

        scene_name = SceneManager.getCurrentSceneName()
        if SystemItemPlusScene.hasOpenItemPlus():
            scene_name = SystemItemPlusScene.getOpenItemPlusName()

        enigma_name = EnigmaManager.getSceneActiveEnigmaName(scene_name)

        if enigma_name is None:
            Trace.log("Entity", 0, "SkipPuzzle - not active enigma at scene {}".format(scene_name))
            SystemMonetization.rollbackGold(component_tag=self.component_id)
            return False

        enigma_params = EnigmaManager.getEnigma(enigma_name)
        enigma_id = enigma_params.id
        self.addSkippedEnigma(enigma_name, enigma_id)

        return False

    def _skipPurchasedEnigma(self, enigma):
        """ used for fast skip MG if player bought skip earlier (fix save bug) """
        _Log("force skip MG - start", optional=True)
        enigma_name = enigma.getEnigmaName()
        enigma_params = EnigmaManager.getEnigma(enigma_name)
        enigma_id = enigma_params.id

        if self.isEnigmaWasSkipped(enigma_name, enigma_id) is True:
            Notification.notify(Notificator.onShiftCollectSkip)
            Notification.notify(Notificator.onEnigmaSkip)
            _Log("enigma {!r} was skipped because skip was bought for it earlier".format(enigma_name))

        return False

    def isEnigmaWasSkipped(self, enigma_name, enigma_id=None):
        items = SystemMonetization.getStorageListValues("skippedMGs")
        if items is None:
            return False

        is_skipped = enigma_id in items or enigma_name in items

        _Log("-- isEnigmaWasSkipped {!r} [{}] in {}: {}".format(enigma_name, enigma_id, items, is_skipped), optional=True)

        return is_skipped

    def addSkippedEnigma(self, enigma_name, enigma_id=None):
        if enigma_name is None:
            if _DEVELOPMENT is True:
                Trace.log("Entity", 0, "addSkippedEnigma: wrong enigma_name (None)")
            return

        if self.isEnigmaWasSkipped(enigma_name, enigma_id) is True:
            return

        SystemMonetization.addStorageListValue("skippedMGs", enigma_id or enigma_name)

    def getProductPrice(self):
        if SystemTutorialFade.is_working is True:
            return 0
        return super(SkipPuzzle, self).getProductPrice()

    def _cleanUp(self):
        self.coin.cleanUp()

    def scopeActivate(self, source, default_task_name):
        if self.demon.isActive() is False:
            self._error("Demon {!r} is not active".format(self.demon.getName()))
            source.addTask(default_task_name)
            return

        def _scopeSuccess(_source):
            source.addTask(default_task_name)

        currency = self.getProductCurrency()
        if currency == "Gold":
            source.addScope(self._system.scopePayGold, descr=self.component_id, scopeSuccess=_scopeSuccess)

        elif currency == "Energy":
            def _filterEnergy(action_name):
                return action_name == self.component_id

            price = self.getProductPrice()
            SystemEnergy = SystemManager.getSystem("SystemEnergy")

            with source.addParallelTask(2) as (tc_response, tc_request):
                with source.addRaceTask(2) as (tc_pay_ok, tc_pay_fail):
                    tc_pay_ok.addListener(Notificator.onEnergyConsumed, Filter=_filterEnergy)
                    tc_pay_ok.addScope(_scopeSuccess)
                    tc_pay_fail.addListener(Notificator.onEnergyNotEnough, Filter=_filterEnergy)
                tc_request.addScope(SystemEnergy.payEnergy, amount=price, action_name=self.component_id)
