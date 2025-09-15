from Foundation.DatabaseManager import DatabaseManager
from Foundation.DefaultManager import DefaultManager
from Foundation.System import System


class SystemEnvironmentSounds(System):
    def __init__(self):
        super(SystemEnvironmentSounds, self).__init__()

        self.ORM_EnvironmentSounds = None
        self.easing = "easyLinear"

        self.currentSounds = {}

        self.EnvironmentSoundFadeIn = DefaultManager.getDefaultFloat("EnvironmentSoundFadeIn", 1.0) * 1000.0
        self.EnvironmentSoundFadeOut = DefaultManager.getDefaultFloat("EnvironmentSoundFadeOut", 1.0) * 1000.0
        pass

    def _onInitialize(self):
        super(SystemEnvironmentSounds, self)._onInitialize()

        self.ORM_EnvironmentSounds = DatabaseManager.getDatabaseORMs("Database", "EnvironmentSounds")
        pass

    def _onRun(self):
        self.addObserver(Notificator.onTransitionBegin, self.__onTransitionBegin)
        self.addObserver(Notificator.onTransitionEnd, self.__onTransitionEnd)

        return True

    def _onStop(self):
        Trace.msg("[SystemEnvironmentSounds] STOP", self.currentSounds)

        for Sound in self.currentSounds.itervalues():
            Mengine.soundStop(Sound)
            pass

        self.currentSounds = {}
        pass

    def __onTransitionBegin(self, sceneFrom, sceneTo, zoomName):
        ORM_OldEnvironmentSound = DatabaseManager.select(self.ORM_EnvironmentSounds, SceneName=sceneFrom)
        ORM_NewEnvironmentSound = DatabaseManager.select(self.ORM_EnvironmentSounds, SceneName=sceneTo)

        OldSoundResources = [ORM.SoundResource for ORM in ORM_OldEnvironmentSound]
        NewSoundResources = [ORM.SoundResource for ORM in ORM_NewEnvironmentSound]

        RemoveSoundResources = set(OldSoundResources) - set(NewSoundResources)

        for SoundResource in RemoveSoundResources:
            if SoundResource is None:
                continue

            if SoundResource in self.currentSounds:
                Sound = self.currentSounds.pop(SoundResource)

                def __stop(isEnd):
                    Trace.fmsg("[SystemEnvironmentSounds] __stop {}", SoundResource)

                    Mengine.soundStop(Sound)
                    pass

                Mengine.soundFadeIn(Sound, self.EnvironmentSoundFadeIn, self.easing, __stop)
                pass
            else:
                Trace.log("System", 0, "self.currentSounds.pop({}) get error".format(SoundResource))
                pass
            pass

        return False

    def __onTransitionEnd(self, sceneFrom, sceneTo, zoomName):
        ORM_OldEnvironmentSound = DatabaseManager.select(self.ORM_EnvironmentSounds, SceneName=sceneFrom)
        ORM_NewEnvironmentSound = DatabaseManager.select(self.ORM_EnvironmentSounds, SceneName=sceneTo)

        OldSoundResources = [ORM.SoundResource for ORM in ORM_OldEnvironmentSound]
        NewSoundResources = [ORM.SoundResource for ORM in ORM_NewEnvironmentSound]

        Trace.fmsg("[SystemEnvironmentSounds] OldSoundResources {}", str(OldSoundResources))
        Trace.fmsg("[SystemEnvironmentSounds] NewSoundResources {}", str(NewSoundResources))
        Trace.fmsg("[SystemEnvironmentSounds] CurrentSounds {}", str(self.currentSounds))

        PlaySoundResources = set(NewSoundResources) - set(OldSoundResources)

        for SoundResource in PlaySoundResources:
            if SoundResource is None:
                continue

            if SoundResource in self.currentSounds:
                continue

            Sound = Mengine.soundFadeOut(SoundResource, True, self.EnvironmentSoundFadeOut, self.easing, None)

            if Sound is None:
                Trace.log("System", 0, "SystemEnvironmentSounds __onTransitionEnd Mengine.soundFadeOut error %s" % (SoundResource))
                continue

            self.currentSounds[SoundResource] = Sound
            pass

        return False
    pass
