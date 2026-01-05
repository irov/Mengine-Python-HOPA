from Foundation.DefaultManager import DefaultManager
from Foundation.Object.DemonObject import DemonObject


class ObjectOptions(DemonObject):
    @staticmethod
    def declareORM(Type):
        DemonObject.declareORM(Type)

        Type.declareParam("MusicVolume")
        Type.declareParam("SoundVolume")
        Type.declareParam("VoiceVolume")
        Type.declareParam("Mute")
        Type.declareParam("Fullscreen")
        Type.declareParam("Widescreen")
        Type.declareParam("Cursor")
        pass

    def _onParams(self, params):
        super(ObjectOptions, self)._onParams(params)

        MusicVolumeValue = DefaultManager.getDefaultFloat('DefaultMusicVolume', 0.5)
        SoundVolumeValue = DefaultManager.getDefaultFloat('DefaultSoundVolume', 0.5)
        VoiceVolumeValue = DefaultManager.getDefaultFloat('DefaultVoiceVolume', 0.5)

        self.initParam("MusicVolume", params, MusicVolumeValue)
        self.initParam("SoundVolume", params, SoundVolumeValue)
        self.initParam("VoiceVolume", params, VoiceVolumeValue)
        self.initParam("Mute", params, False)
        self.initParam("Fullscreen", params, True)
        self.initParam("Widescreen", params, False)
        self.initParam("Cursor", params, False)
        pass
    pass
