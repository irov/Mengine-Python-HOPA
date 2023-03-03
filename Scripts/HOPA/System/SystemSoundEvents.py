from Foundation.System import System
from HOPA.SoundEffectManager import SoundEffectManager
from Notification import Notification


class SystemSoundEvents(System):
    def _onParams(self, params):
        super(SystemSoundEvents, self)._onParams(params)
        self.events = []
        self.observers = []
        pass

    def _onRun(self):
        self.events = SoundEffectManager.getEventSounds()

        for notify, soundName in self.events.items():
            self.addObserver(notify, soundName)
            pass

        return True
        pass

    def addObserver(self, notify, soundName):
        def _onSound(*Args):
            Mengine.soundPlay(soundName, False, None)
            return False
            pass

        identity = Notificator.getIdentity(notify)
        observer = Notification.addObserver(identity, _onSound)
        self.observers.append(observer)
        pass

    def _onStop(self):
        for observer in self.observers:
            Notification.removeObserver(observer)
            pass
        pass

    pass
