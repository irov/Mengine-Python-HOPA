from Foundation.DatabaseManager import DatabaseManager


class SoundEffectManager(object):
    s_soundEffects = {}

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            Event = record.get("Event")
            Sound = record.get("Sound")

            if Mengine.hasSound(Sound) is False:
                Trace.log("Manager", 0, "SoundEffectManager.loadSoundEffect '%s' not found sound '%s' for event '%s'" % (param, Sound, Event))
                continue

            SoundEffectManager.s_soundEffects[Event] = Sound

        return True

    @staticmethod
    def getEventSounds():
        return SoundEffectManager.s_soundEffects

    @staticmethod
    def onDeactivate():
        pass
