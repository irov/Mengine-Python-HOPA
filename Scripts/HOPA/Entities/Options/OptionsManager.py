from Foundation.DatabaseManager import DatabaseManager
from Foundation.DefaultManager import DefaultManager
from Foundation.GroupManager import GroupManager


XlsxOptionsSoundVolumeCheck = "OptionsSoundVolumeCheck"


class SoundCheckParam(object):
    def __init__(self, soundType, sliderMovieName, sliderMovieSlotName, playButtonPrototype, stopButtonPrototype,
                 checkSoundTracklist):
        self.soundType = soundType
        self.sliderMovieName = sliderMovieName
        self.sliderMovieSlotName = sliderMovieSlotName
        self.playButtonPrototype = playButtonPrototype
        self.stopButtonPrototype = stopButtonPrototype
        self.checkSoundTracklist = checkSoundTracklist


class OptionsManager(object):
    s_options = {}
    s_scrollBars = {}

    s_soundCheckParams = []

    @staticmethod
    def onFinalize():
        OptionsManager.s_options = {}

    @staticmethod
    def loadParams(module, param):
        SlidersName = ['Voice', 'Music', 'Sound']
        for name in SlidersName:
            slider = GroupManager.getObject('Options', 'Movie2Scrollbar_{}'.format(name))
            Volume = DefaultManager.getDefaultFloat('Default{}Volume'.format(name), 0.5)
            OptionsManager.s_scrollBars[name] = [Volume, slider]

        """ SoundType SliderbarMovie SliderbarMovie_Slot PlayButtonPrototype StopButtonPrototype [CheckSoundTracklist] """
        records = DatabaseManager.getDatabaseRecords(module, XlsxOptionsSoundVolumeCheck)
        if records is not None:
            params = []

            for record in records:
                soundType = record.get("SoundType")
                slider = record.get("SliderbarMovie")
                slot = record.get("SliderbarMovie_Slot")
                playButton = record.get("PlayButtonPrototype")
                stopButton = record.get("StopButtonPrototype")
                checkSoundList = record.get("CheckSoundTracklist", [])

                param = SoundCheckParam(soundType, slider, slot, playButton, stopButton, checkSoundList)
                params.append(param)

            OptionsManager.s_soundCheckParams = params

        else:
            msg = "[Warning] OptionsManager cant find {} database. Please, consider to add one"
            msg = msg.format(XlsxOptionsSoundVolumeCheck)
            Trace.log("Manager", 0, msg)

        return True

    @staticmethod
    def getSoundCheckParams():
        return OptionsManager.s_soundCheckParams

    @staticmethod
    def getScrollBars():
        return OptionsManager.s_scrollBars
