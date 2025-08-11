from Foundation.Manager import Manager

from Foundation.DatabaseManager import DatabaseManager
from Foundation.DefaultManager import DefaultManager
from Foundation.GroupManager import GroupManager

class OptionsManager(Manager):
    s_options = {}
    s_scrollBars = {}

    s_soundCheckParams = []

    class SoundCheckParam(object):
        def __init__(self, soundType, sliderMovieName, sliderMovieSlotName, playButtonPrototype, stopButtonPrototype,
                     checkSoundTracklist):
            self.soundType = soundType
            self.sliderMovieName = sliderMovieName
            self.sliderMovieSlotName = sliderMovieSlotName
            self.playButtonPrototype = playButtonPrototype
            self.stopButtonPrototype = stopButtonPrototype
            self.checkSoundTracklist = checkSoundTracklist

    @staticmethod
    def _onFinalize():
        OptionsManager.s_options = {}
        OptionsManager.s_scrollBars = {}
        OptionsManager.s_soundCheckParams = []
        pass

    @staticmethod
    def loadParams(module, param):
        if param == "Options":
            OptionsManager._loadScrollBarParams(module, param)
        elif param == "OptionsSoundVolumeCheck":
            OptionsManager._loadSoundCheckParams(module, param)

        return True

    @staticmethod
    def _loadScrollBarParams(module, param):
        SlidersName = ['Voice', 'Music', 'Sound']
        for name in SlidersName:
            slider_name = 'Movie2Scrollbar_{}'.format(name)

            if GroupManager.hasObject('Options', slider_name) is False:
                # if _DEVELOPMENT is True:
                #     Trace.log("Manager", 0, "OptionsManager can't find slider {!r}".format(slider_name))
                continue

            slider = GroupManager.getObject('Options', slider_name)
            Volume = DefaultManager.getDefaultFloat('Default{}Volume'.format(name), 0.5)
            OptionsManager.s_scrollBars[name] = [Volume, slider]

    @staticmethod
    def _loadSoundCheckParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        if records is None:
            msg = "[Warning] OptionsManager cant find {} database. Please, consider to add one"
            msg = msg.format(param)
            Trace.log("Manager", 0, msg)
            return

        params = []

        for record in records:
            """ SoundType SliderbarMovie SliderbarMovie_Slot PlayButtonPrototype StopButtonPrototype [CheckSoundTracklist] """

            soundType = record.get("SoundType")
            slider = record.get("SliderbarMovie")
            slot = record.get("SliderbarMovie_Slot")
            playButton = record.get("PlayButtonPrototype")
            stopButton = record.get("StopButtonPrototype")
            checkSoundList = record.get("CheckSoundTracklist", [])

            if soundType not in OptionsManager.s_scrollBars:
                msg = "[Warning] OptionsManager cant find slider option for {!r}. Impossible to setup sound checker."
                msg = msg.format(soundType)
                Trace.log("Manager", 0, msg)
                continue

            param = OptionsManager.SoundCheckParam(soundType, slider, slot, playButton, stopButton, checkSoundList)
            params.append(param)

        OptionsManager.s_soundCheckParams = params

    @staticmethod
    def getSoundCheckParams():
        return OptionsManager.s_soundCheckParams

    @staticmethod
    def getScrollBars():
        return OptionsManager.s_scrollBars
