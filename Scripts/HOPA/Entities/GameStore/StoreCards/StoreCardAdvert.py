from Foundation.MonetizationManager import MonetizationManager
from Foundation.SystemManager import SystemManager
from Foundation.Utils import calcTime
from Foundation.Providers.AdvertisementProvider import AdvertisementProvider
from HOPA.Entities.GameStore.StoreCards.StoreCardMixin import StoreCardMixin

class StoreCardAdvert(StoreCardMixin):
    unblock_timestamp = None
    TIME_BLOCK_EVENT = Event("onTimeBlock")
    PRICE_TEMPLATE = "{text}"

    def __init__(self):
        super(StoreCardAdvert, self).__init__()
        self.timer = None

    def init(self, card_id, card_movie, image_movie, params):
        super(StoreCardAdvert, self).init(card_id, card_movie, image_movie, params)

        self.refreshTimeBlock()

    def _onEnable(self):
        if AdvertisementProvider.hasRewardedAdvert() is True:
            # check if already blocked by time delay,
            # but if not - we can unblock it
            if self.timer is None:
                self.setBlock(False)
        else:
            # no available ads - block button
            self.setBlock(True)

    def _setPrice(self):
        advert_text_id = MonetizationManager.getGeneralSetting("AdvertPriceTextID")
        advert_text = Mengine.getTextFromId(advert_text_id)
        Mengine.setTextAliasArguments(self.env, self.ALIAS_PRICE, self.PRICE_TEMPLATE.format(text=advert_text))

    def _getRewardArg(self):
        advert_prod_id = MonetizationManager.getGeneralSetting("AdvertProductID")
        if advert_prod_id is not None:
            gold_per_ad = MonetizationManager.getProductReward(advert_prod_id, "Gold")
        else:
            gold_per_ad = MonetizationManager.getGeneralSetting("GoldPerAd")

        return gold_per_ad

    def refreshTimeBlock(self):
        if self.unblock_timestamp is None:
            return

        if self.unblock_timestamp - Mengine.getTimeMs() / 1000 <= 0:
            self.setTimeBlock(False)
        else:
            self.setTimeBlock(True)

    def _onTimer(self, time):
        time_left = self.unblock_timestamp - Mengine.getTime()

        _, hours, min, sec = calcTime(time_left)

        Mengine.setTextAliasArguments(self.env, self.ALIAS_PRICE, "{}:{}:{}".format(hours, min, sec))
        if time_left <= 0:
            self.setTimeBlock(False)

    def setTimeBlock(self, state):
        SystemMonetization = SystemManager.getSystem("SystemMonetization")
        if SystemMonetization.isAdsEnded() is True:
            return True

        self.TIME_BLOCK_EVENT(state)

        if state is True:
            delay = MonetizationManager.getGeneralSetting("DelayBetweenAdView")

            timer_text_id = MonetizationManager.getGeneralSetting("AdDelayTimerTextID", "ID_TEXT_GAMESTORE_AD_TIMER")
            Mengine.setTextAlias(self.env, self.ALIAS_PRICE, timer_text_id)
            _, hours, min, sec = calcTime(delay)
            Mengine.setTextAliasArguments(self.env, self.ALIAS_PRICE, "{}:{}:{}".format(hours, min, sec))

            if self.timer is not None:
                if _DEVELOPMENT:
                    Trace.log("Entity", 0, "Why you set time block when it was already in time block?")
                Mengine.removeChronometer(self.timer)

            if self.unblock_timestamp is None:
                StoreCardAdvert.unblock_timestamp = Mengine.getTimeMs() / 1000 + delay

            self.timer = Mengine.addChronometer(self._onTimer)

            self.setBlock(True)
            return True

        if state is False:
            if self.timer is not None:
                Mengine.removeChronometer(self.timer)
                self.timer = None

            StoreCardAdvert.unblock_timestamp = None

            self.setBlock(False)
            self._setPrice()
            return True

        return False

    def cleanUp(self):
        super(StoreCardAdvert, self).cleanUp()

        if self.timer is not None:
            Mengine.removeChronometer(self.timer)
            self.timer = None

        self.TIME_BLOCK_EVENT.removeObservers()

    # scopes

    def _scopeInteract(self, source):
        source.addTask("AliasShowRewardedAdvert", AdPlacement="rewarded", WhileShowScope=self._scopeAfterView)

    def _scopeAfterView(self, source):
        if MonetizationManager.getGeneralSetting("DelayBetweenAdView") is None:
            source.addDummy()
            return

        with source.addRaceTask(2) as (viewed, hidden):
            viewed.addListener(Notificator.onAdvertRewarded)
            viewed.addFunction(self.setTimeBlock, True)
            # viewed.addPrint("  - viewed")

            hidden.addListener(Notificator.onAdvertHidden)
            hidden.addDelay(0)  # fix: setTimeBlock has no time for call  # hidden.addPrint("  - hidden")

    def _scopeInteractDummy(self, source):
        source.addPrint("<GameStore> [{}] Dummy show ad - wait response".format(self.card_id))
