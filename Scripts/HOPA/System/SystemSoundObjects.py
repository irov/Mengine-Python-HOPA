from Foundation.System import System
from HOPA.SoundObjectsManager import SoundObjectsManager
from Notification import Notification


class SystemSoundObjects(System):
    def _onParams(self, params):
        super(SystemSoundObjects, self)._onParams(params)
        self.events = []
        self.observers = []
        pass

    def _onRun(self):
        self.events = SoundObjectsManager.getSoundObjects()

        for notify, soundObjects in self.events.items():
            self.addObserver(notify, soundObjects)
            pass
        pass

    def addObserver(self, notify, soundObjects):
        def _onSound(curObject):
            for soundObject in soundObjects:
                if soundObject.getObject() != curObject:
                    continue
                    pass
                soundName = soundObject.getSound()
                Mengine.soundPlay(soundName, False, None)
                pass

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
