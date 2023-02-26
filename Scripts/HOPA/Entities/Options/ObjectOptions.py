from Foundation.DefaultManager import DefaultManager
from Foundation.Object.DemonObject import DemonObject

class ObjectOptions(DemonObject):
    def _onParams(self, params):
        super(ObjectOptions, self)._onParams(params)
        MusicVolumeValue = DefaultManager.getDefaultFloat('DefaultMusicVolume', 0.5)
        SoundVolumeValue = DefaultManager.getDefaultFloat('DefaultSoundVolume', 0.5)
        VoiceVolumeValue = DefaultManager.getDefaultFloat('DefaultVoiceVolume', 0.5)

        self.params["MusicVolume"] = params.get("MusicVolume", MusicVolumeValue)
        self.params["SoundVolume"] = params.get("SoundVolume", SoundVolumeValue)
        self.params["VoiceVolume"] = params.get("VoiceVolume", VoiceVolumeValue)
        self.params["Mute"] = params.get("Mute", False)
        self.params["Fullscreen"] = params.get("Fullscreen", True)
        self.params["Widescreen"] = params.get("WideScreen", False)
        self.params["Cursor"] = params.get("Cursor", False)
        pass
    pass