from Foundation.System import System
from Notification import Notification


class SystemSounds(System):
    notifyList = [
        Notificator.onButtonSoundClick,
        Notificator.onButtonSoundEnter,
        Notificator.onSocketSoundClick,
        Notificator.onSocketSoundEnter
    ]

    def _onParams(self, params):
        super(SystemSounds, self)._onParams(params)
        self.observers = []
        pass

    def _onRun(self):
        for notify in SystemSounds.notifyList:
            observer = Notification.addObserver(notify, self._onSound)
            self.observers.append(observer)
            pass
        return True
        pass

    def _onSound(self, soundName):
        if Mengine.hasSound(soundName) is False:
            return False
            pass

        Mengine.soundPlay(soundName, False, None)

        return False
        pass

    def _onStop(self):
        for observer in self.observers:
            Notification.removeObserver(observer)
            pass
        pass

    pass
