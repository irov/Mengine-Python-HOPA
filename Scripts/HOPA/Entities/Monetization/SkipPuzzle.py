from Foundation.PolicyManager import PolicyManager
from Foundation.Systems.SystemMonetization import SystemMonetization
from Foundation.Utils import SimpleLogger
from HOPA.EnigmaManager import EnigmaManager
from HOPA.Entities.Monetization.BaseComponent import BaseComponent
from HOPA.Entities.Monetization.Coin import Coin
from HOPA.System.SystemItemPlusScene import SystemItemPlusScene
from HOPA.System.SystemTutorialFade import SystemTutorialFade


_Log = SimpleLogger("PaidSkipPuzzle")


class SkipPuzzle(BaseComponent):
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

        scene_name = None
        if SystemItemPlusScene.hasOpenItemPlus():
            scene_name = SystemItemPlusScene.getOpenItemPlusName()

        enigma_name = EnigmaManager.getSceneActiveEnigmaName(scene_name)
        enigma_params = EnigmaManager.getEnigma(enigma_name)
        enigma_id = enigma_params.id
        self.addSkippedEnigma(enigma_name, enigma_id)

        return False

    def _skipPurchasedEnigma(self, enigma):
        """ used for fast skip MG if player bought skip earlier (fix save bug) """
        _Log("force skip MG - start")
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

        _Log("-- isEnigmaWasSkipped {!r} [{}] in {}: {}".format(enigma_name, enigma_id, items, is_skipped))

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
