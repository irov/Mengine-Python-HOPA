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
        pass

    def _onStop(self):
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

                # print "SystemEnvironmentSounds __onTransitionBegin  FadeIn", SoundResource

                Mengine.soundFadeIn(Sound, self.EnvironmentSoundFadeIn, self.easing, None)
                pass
            else:
                Trace.log("System", 0, "self.currentSounds.pop(SoundResource) get error")
                pass
            pass

        return False
        pass

    def __onTransitionEnd(self, sceneFrom, sceneTo, zoomName):
        ORM_OldEnvironmentSound = DatabaseManager.select(self.ORM_EnvironmentSounds, SceneName=sceneFrom)
        ORM_NewEnvironmentSound = DatabaseManager.select(self.ORM_EnvironmentSounds, SceneName=sceneTo)

        OldSoundResources = [ORM.SoundResource for ORM in ORM_OldEnvironmentSound]
        NewSoundResources = [ORM.SoundResource for ORM in ORM_NewEnvironmentSound]

        PlaySoundResources = set(NewSoundResources) - set(OldSoundResources)

        for SoundResource in PlaySoundResources:
            if SoundResource is None:
                continue
                pass

            if SoundResource in self.currentSounds:
                Sound = self.currentSounds.pop(SoundResource)
                Mengine.soundStop(Sound)
                pass

            # Sound = Mengine.soundFadeOut(str(SoundResource), True, self.EnvironmentSoundFadeOut,  self.easing, self.test_Print) #reprARHANOID
            Sound = Mengine.soundFadeOut(str(SoundResource), True, self.EnvironmentSoundFadeOut, self.easing, self.test_Print)

            self.currentSounds[SoundResource] = Sound
            pass

        return False
        pass
    def test_Print(self, a=1, b=2):
        pass

    pass