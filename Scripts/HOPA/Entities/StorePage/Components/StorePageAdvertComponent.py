from Foundation.MonetizationManager import MonetizationManager
from Foundation.Providers.AdvertisementProvider import AdvertisementProvider
from Foundation.Systems.SystemMonetization import SystemMonetization
from Foundation.Utils import calcTime
from HOPA.Entities.StorePage.Components.StorePageBaseComponent import StorePageBaseComponent


class StorePageAdvertComponent(StorePageBaseComponent):

    OFFER_RETRY_DELAY = 1000

    def __init__(self, page, button):
        super(StorePageAdvertComponent, self).__init__(page)

        self.button = button
        self.timer = None
        self.reset_timestamp = None
        self.offer_timer = None
        self.next_offer_check = 0

    def _run(self):
        self.handleAdvertButton()
        self.handleAdvertCounter()

    def _cleanUp(self):
        self.removeAdvertTimer()
        self.removeOfferTimer()
        self.button = None

    def _check(self):
        advert_buttons = filter(lambda btn: btn.action == "advert", self.page.buttons)
        if len(advert_buttons) != 1:
            Trace.log("Entity", 0, "StorePage [{}] should have one advert button (1 != {})".format(self.page.PageID,
                                                                                                   len(advert_buttons)))
            return False
        return True

    # --- advert counter -----------------------------------------------------------------------------------------------

    def _cbAdvertHidden(self, *args):
        self.updateAdvertCounter()
        return False

    def _cbRewardedAdUserRewarded(self, params):
        if params.get("placement") != self.button.getAdvertName():
            return False

        self.updateAdvertCounter()
        return False

    def updateAdvertCounter(self):
        ad_name = self.button.getAdvertName()
        key_viewed_ads = SystemMonetization.getAdvertStorageKey(ad_name, "today_viewed_ads")
        viewed_ads = int(SystemMonetization.getStorageValue(key_viewed_ads))
        max_ads = MonetizationManager.getGeneralSetting("AdsPerDay")    # todo: make it unique for each ad unit

        self.button.updateCounter(viewed_ads, max_ads)

    def handleAdvertCounter(self):
        self.updateAdvertCounter()
        self.addObserver(Notificator.onAdvertHidden, self._cbAdvertHidden)
        self.addObserver(Notificator.onRewardedAdUserRewarded, self._cbRewardedAdUserRewarded)

    # --- advert button ------------------------------------------------------------------------------------------------

    def _cbAvailableAdsNew(self, ad_name):
        if self.button.getAdvertName() != ad_name:
            return False

        self.updateAdvertCounter()
        self.removeAdvertTimer()
        self.checkOffer()
        return False

    def _cbAvailableAdsEnded(self, ad_name):
        if self.button.getAdvertName() != ad_name:
            return False

        self.updateAdvertCounter()
        self.removeOfferTimer()
        self.startAdvertTimer()
        self.button.setBlock(True)
        return False

    def handleAdvertButton(self):
        advert_button = self.button

        if SystemMonetization.isAdsEnded(advert_button.getAdvertName()) is True:
            advert_button.setBlock(True)
            self.startAdvertTimer()
        else:
            self.checkOffer()

        self.addObserver(Notificator.onAvailableAdsNew, self._cbAvailableAdsNew)
        self.addObserver(Notificator.onAvailableAdsEnded, self._cbAvailableAdsEnded)

    def calcAdvertResetTimestamp(self):
        """ returns timestamp when time will be 12:00 AM """

        time = Mengine.getLocalDateStruct()
        hours, min, sec = time.hour, time.minute, time.second

        unblock_timestamp = Mengine.getTime()
        unblock_timestamp += (23 - hours) * 60 * 60
        unblock_timestamp += (59 - min) * 60
        unblock_timestamp += (60 - sec)

        return unblock_timestamp

    def startAdvertTimer(self):
        self.removeOfferTimer()
        if self.timer is not None:
            self.removeAdvertTimer()
        self.reset_timestamp = self.calcAdvertResetTimestamp()
        self.timer = Mengine.addChronometer(self._onTimer)

    def removeAdvertTimer(self):
        if self.timer is None:
            return
        Mengine.removeChronometer(self.timer)
        self.timer = None
        self.reset_timestamp = None

        self.updateTimerText()

        SystemMonetization.updateAvailableAds()

    def checkOffer(self):
        ad_name = self.button.getAdvertName()
        if AdvertisementProvider.canOfferRewardedAdvert(ad_name) is False:
            # fixme: get localized text
            no_offer_text = "no offer now"
            self.button.updateTimer(no_offer_text)
            self.button.setBlock(True)
            self.startOfferTimer()
            return False

        self.removeOfferTimer()
        self.button.updateTimer("")
        self.button.setBlock(False)
        return True

    def startOfferTimer(self):
        if self.offer_timer is not None:
            return
        self.next_offer_check = 0
        self.offer_timer = Mengine.addChronometer(self._onOfferTimer)

    def removeOfferTimer(self):
        if self.offer_timer is None:
            return
        Mengine.removeChronometer(self.offer_timer)
        self.offer_timer = None
        self.next_offer_check = 0

    def _onOfferTimer(self, time):
        now = Mengine.getTimeMs()
        if now < self.next_offer_check:
            return
        self.next_offer_check = now + self.OFFER_RETRY_DELAY
        self.checkOffer()

    def updateTimerText(self, h=0, m=0, s=0):
        text = "{}h {}m {}s".format(h, m, s)
        self.button.updateTimer(text)

    def _onTimer(self, time):
        time_left = self.reset_timestamp - Mengine.getTime()

        if time_left <= 0:
            self.removeAdvertTimer()
            return

        _, hours, minutes, seconds = calcTime(time_left)
        self.updateTimerText(hours, minutes, seconds)
