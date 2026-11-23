from Foundation.Providers.LocalNotificationsProvider import LocalNotificationsProvider
from Foundation.System import System
from Foundation.SystemManager import SystemManager
from HOPA.System.SystemEnergy import SystemEnergy

NOTIFICATION_NAME = "energy_full"


class SystemEnergyNotification(System):
    """ Keeps the 'energy_full' local notification armed with the time left until energy is fully refilled.
        The notification itself (texts, platforms) is configured in the project deploy. """

    def _onRun(self):
        if SystemEnergy.isEnable() is False:
            return True

        self.addObserver(Notificator.onUpdateEnergyBalance, self._cbEnergyChanged)
        # iOS schedules before entering the background, so keep the delay current on balance updates.
        self.addObserver(Notificator.onApplicationDidEnterBackground, self._cbEnergyChanged)

        self._updateNotification()
        return True

    def _onStop(self):
        LocalNotificationsProvider.setNotificationDelay(NOTIFICATION_NAME, 0)

    def _cbEnergyChanged(self, *args):
        self._updateNotification()
        return False

    def _updateNotification(self):
        seconds = 0
        if SystemManager.hasSystem("SystemEnergy") is True:
            system_energy = SystemManager.getSystem("SystemEnergy")
            seconds = system_energy.getSecondsToFullEnergy()

        LocalNotificationsProvider.setNotificationDelay(NOTIFICATION_NAME, seconds)
