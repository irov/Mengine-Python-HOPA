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
        self.addObserver(Notificator.onEnergyRecharge, self._cbEnergyChanged)
        self.addObserver(Notificator.onEnergyCharged, self._cbEnergyChanged)
        # last refresh before background; iOS schedules before this event, so the observers above keep the delay current
        self.addObserver(Notificator.onApplicationDidEnterBackground, self._cbEnergyChanged)

        self._updateNotification()
        return True

    def _onStop(self):
        LocalNotificationsProvider.setNotificationDelay(NOTIFICATION_NAME, 0)

    def _cbEnergyChanged(self, *args):
        self._updateNotification()
        return False

    def _updateNotification(self):
        seconds = self._calcSecondsToFullEnergy()
        LocalNotificationsProvider.setNotificationDelay(NOTIFICATION_NAME, seconds)

    @staticmethod
    def _calcSecondsToFullEnergy():
        if SystemEnergy.isInfinityMode() is True:
            return 0

        if SystemManager.hasSystem("SystemEnergy") is False:
            return 0

        system_energy = SystemManager.getSystem("SystemEnergy")
        if system_energy.current_energy is None:
            return 0

        missing_energy = SystemEnergy.getMaxEnergy() - system_energy.current_energy
        if missing_energy <= 0:
            return 0

        refill_time = SystemEnergy.s_settings["refill_time"]
        refill_per_time = max(SystemEnergy.s_settings["refill_per_time"], 1)
        ticks = (missing_energy + refill_per_time - 1) // refill_per_time

        cooldown_timestamp = system_energy.cooldown_timestamp
        if cooldown_timestamp is None:
            return ticks * refill_time

        next_tick = cooldown_timestamp - Mengine.getTime()
        if next_tick <= 0:
            # the tick is due: SystemEnergy refills (this notify) and only then reloads the cooldown (+1 s)
            next_tick = refill_time + 1

        return next_tick + (ticks - 1) * refill_time
