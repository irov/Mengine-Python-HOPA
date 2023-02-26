from Foundation.MonetizationManager import MonetizationManager
from Foundation.Providers.AdvertisementProvider import AdvertisementProvider
from Foundation.Systems.SystemMonetization import SystemMonetization
from Foundation.Utils import calcTime
from HOPA.Entities.StorePage.Components.StorePageBaseComponent import StorePageBaseComponent

class StorePageAdvertComponent(StorePageBaseComponent):

    def __init__(self, page, button):
        super(StorePageAdvertComponent, self).__init__(page)

        self.button = button
        self.timer = None
        self.reset_timestamp = None

    def _run(self):
        self.handleAdvertButton()
        self.handleAdvertCounter()

    def _cleanUp(self):
        self.removeAdvertTimer()
        self.button = None

    def _check(self):
        advert_buttons = filter(lambda btn: btn.action == "advert", self.page.buttons)
        if len(advert_buttons) != 1:
            Trace.log("Entity", 0, "StorePage [{}] should have one advert button (1 != {})".format(self.page.PageID, len(advert_buttons)))
            return False
        return True

    # --- advert counter -----------------------------------------------------------------------------------------------

    def _cbAdvertHidden(self, *args):
        self.updateAdvertCounter()
        return False

    def updateAdvertCounter(self):
        viewed_ads = int(SystemMonetization.getStorageValue("todayViewedAds"))
        max_ads = MonetizationManager.getGeneralSetting("AdsPerDay")

        self.button.updateCounter(viewed_ads, max_ads)

    def handleAdvertCounter(self):
        self.updateAdvertCounter()
        self.addObserver(Notificator.onAdvertHidden, self._cbAdvertHidden)

    # --- advert button ------------------------------------------------------------------------------------------------

    def _cbAvailableAdsNew(self, *args):
        self.updateAdvertCounter()
        self.removeAdvertTimer()
        self.button.setBlock(False)
        return False

    def _cbAvailableAdsEnded(self, *args):
        self.updateAdvertCounter()
        self.startAdvertTimer()
        self.button.setBlock(True)
        return False

    def handleAdvertButton(self):
        advert_button = self.button

        self.checkOffer()

        if advert_button.id not in self.page.WaitButtons:
            advert_button.setBlock(True)
            self.startAdvertTimer()

        self.addObserver(Notificator.onAvailableAdsNew, self._cbAvailableAdsNew)
        self.addObserver(Notificator.onAvailableAdsEnded, self._cbAvailableAdsEnded)

    def calcAdvertResetTimestamp(self):
        """ returns timestamp when time will be 12:00 AM """

        time = Mengine.getLocalDateStruct()
        hours, min, sec = time.hour, time.minute, time.second

        unblock_timestamp = Mengine.getTimeMs() / 1000
        unblock_timestamp += (23 - hours) * 60 * 60
        unblock_timestamp += (59 - min) * 60
        unblock_timestamp += (60 - sec)

        return unblock_timestamp

    def startAdvertTimer(self):
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
        if AdvertisementProvider.canOfferAdvert("Rewarded") is False:
            # fixme: get localized text
            no_offer_text = "no offer now"
            self.button.updateTimer(no_offer_text)
            self.button.setBlock(True)
        else:
            self.button.setBlock(False)

    def updateTimerText(self, h=0, m=0, s=0):
        text = "{}h {}m {}s".format(h, m, s)
        self.button.updateTimer(text)

    def _onTimer(self, timer_id, timestamp):
        if timer_id != self.timer:
            return
        timestamp /= 1000

        time_left = self.reset_timestamp - timestamp

        if time_left <= 0:
            self.removeAdvertTimer()
            return

        _, hours, min, sec = calcTime(time_left)
        self.updateTimerText(hours, min, sec)