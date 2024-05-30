from HOPA.Entities.BalanceIndicator.IndicatorMixin import IndicatorMixin
from Foundation.MonetizationManager import MonetizationManager
from Foundation.SystemManager import SystemManager


class AdvertisementIndicator(IndicatorMixin):
    type = "Advertisement"
    icon_tag = "AdvertisementReady"
    ad_name = "Rewarded"
    identity = Notificator.onAvailableAdsNew

    def prepare(self, parent, icon_provider_object):
        # todo: rm duplicated code

        if MonetizationManager.getGeneralSetting("AdvertisementBalanceIndicatorEnable", False) is False:
            return True

        bg_name = self._getBackgroundName()
        if parent.hasObject(bg_name) is False:
            Trace.log("Entity", 0, "Indicator {!r} - not found object {!r} in {}"
                      .format(self.type, bg_name, parent.getName()))
            return False

        icon_name = self._getIconName()
        if parent.hasPrototype(icon_name) is False:
            Trace.log("Entity", 0, "Indicator {!r} - not found prototype {!r} in {}"
                      .format(self.type, icon_name, parent.getName()))
            return False

        bg_movie = parent.getObject(bg_name)
        object_name = "Movie2_{}".format(self.type)
        try:
            icon_movie = parent.generateIcon(object_name, icon_name, Enable=True)
        except AttributeError:
            icon_movie = parent.generateObjectUnique(object_name, icon_name, Enable=True)

        icon_node = icon_movie.getEntityNode()
        icon_node.removeFromParent()
        # we can't do properly slot check, so just addChild and pray that it would be ok
        bg_movie.addChildToSlot(icon_node, "icon")
        bg_movie.setBlock(self._isAdsEnded() is True)
        bg_movie.setEnable(True)

        self.bg_movie = bg_movie
        self.icon_movie = icon_movie

        self.observers = [
            Notification.addObserver(Notificator.onAvailableAdsNew, self._cbAvailableAdsNew),
            Notification.addObserver(Notificator.onAvailableAdsEnded, self._cbAvailableAdsEnded),
        ]

        return True

    def _cbAvailableAdsNew(self, ad_name):
        if self.ad_name != ad_name:
            return False
        self.bg_movie.setBlock(False)
        return False

    def _cbAvailableAdsEnded(self, ad_name):
        if self.ad_name != ad_name:
            return False
        self.bg_movie.setBlock(True)
        return False

    def _isAdsEnded(self):
        if SystemManager.hasSystem("SystemMonetization") is False:
            Trace.log("Entity", 0, "SystemMonetization not found to check is Ads Ended!!")
            return True

        SystemMonetization = SystemManager.getSystem("SystemMonetization")
        return SystemMonetization.isAdsEnded(self.ad_name) is True

    def scopeClick(self, source):
        source.addBlock()
