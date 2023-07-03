from Foundation.DemonManager import DemonManager
from Foundation.GroupManager import GroupManager
from Foundation.System import System


class SystemOptions(System):
    OPTIONS_GROUP = "Options"
    OPTIONS_OBJECT = "Demon_Options"

    def __init__(self):
        super(SystemOptions, self).__init__()
        self.Demon_Options = None
        self.language = None

    def _onInitialize(self):
        Options = GroupManager.getGroup(self.OPTIONS_GROUP)
        if _DEVELOPMENT is True and Options is None:
            self.initializeFailed("invalid group '%s'" % self.OPTIONS_GROUP)

        self.Demon_Options = Options.getObject(self.OPTIONS_OBJECT)
        if _DEVELOPMENT is True and self.Demon_Options is None:
            self.initializeFailed("invalid object '%s:%s'" % (self.OPTIONS_GROUP, self.OPTIONS_OBJECT))

    def _onRun(self):
        self.addObserver(Notificator.onFullscreen, self._onFullscreenFilter)
        self.addObserver(Notificator.onFixedContentResolution, self._onWidescreenFilter)
        self.addObserver(Notificator.onCursorMode, self._onCursorFilter)
        self.addObserver(Notificator.onMute, self._onMuteFilter)
        self.addObserver(Notificator.onMusicVolume, self._onMusicVolumeFilter)
        self.addObserver(Notificator.onSoundVolume, self._onSoundVolumeFilter)
        self.addObserver(Notificator.onVoiceVolume, self._onVoiceVolumeFilter)
        self.addObserver(Notificator.onSessionNew, self._onSessionNew)

        return True

    def _onSessionNew(self, accountID):
        if Mengine.hasCurrentAccount() is False:
            return False

        Cursor = Mengine.getCurrentAccountSettingBool("Cursor")
        if Cursor is not None:
            self.Demon_Options.setParam("Cursor", Cursor)

        Fullscreen = Mengine.getCurrentAccountSettingBool("Fullscreen")
        if Fullscreen is not None:
            self.Demon_Options.setParam("Fullscreen", Fullscreen)

        Widescreen = Mengine.getCurrentAccountSettingBool("Widescreen")
        if Widescreen is not None:
            self.Demon_Options.setParam("Widescreen", Widescreen)

        Mute = Mengine.getCurrentAccountSettingBool("Mute")
        if Mute is not None:
            self.Demon_Options.setParam("Mute", Mute)

        MusicVolume = Mengine.getCurrentAccountSettingFloat("MusicVolume")
        if MusicVolume is not None:
            self.Demon_Options.setParam("MusicVolume", MusicVolume)

        SoundVolume = Mengine.getCurrentAccountSettingFloat("SoundVolume")
        if SoundVolume is not None:
            self.Demon_Options.setParam("SoundVolume", SoundVolume)

        VoiceVolume = Mengine.getCurrentAccountSettingFloat("VoiceVolume")
        if VoiceVolume is not None:
            self.Demon_Options.setParam("VoiceVolume", VoiceVolume)

        return False

    def _onFullscreenFilter(self, value):
        self.Demon_Options.setParam("Fullscreen", value)
        return False

    def _onWidescreenFilter(self, value):
        self.Demon_Options.setParam("Widescreen", value)
        return False

    def _onCursorFilter(self, value):
        self.Demon_Options.setParam("Cursor", value)
        return False

    def _onMuteFilter(self, value):
        self.Demon_Options.setParam("Mute", value)
        return False

    def _onMusicVolumeFilter(self, value):
        # self.Demon_Options.setParam("MusicVolume", value)
        return False

    def _onSoundVolumeFilter(self, value):
        # self.Demon_Options.setParam("SoundVolume", value)
        return False

    def _onVoiceVolumeFilter(self, value):
        # self.Demon_Options.setParam("VoiceVolume", value)
        return False

    def _onSave(self):
        return self.language

    def _onLoad(self, language):
        self.language = language

        ''' Language Select, Apply Current Saved Language On Start '''
        if DemonManager.hasDemon("LanguageSelect"):
            if self.language is not None and str(Mengine.getLocale()) != self.language:
                Mengine.setLocale(self.language)
