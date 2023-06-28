from Foundation.DefaultManager import DefaultManager
from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.GroupManager import GroupManager
from Foundation.GuardBlockInput import GuardBlockInput
from Foundation.TaskManager import TaskManager
from HOPA.Entities.Options.OptionsCheckSound import CheckSoundController
from HOPA.Entities.Options.OptionsManager import OptionsManager
from Notification import Notification


BUTTON_LANGUAGE_SELECT_NAME = "Movie2Button_LanguageSelect"


class Options(BaseEntity):
    s_start_volume_values = []
    startMusicVolumeValue = 0
    startSoundVolumeValue = 0
    startVoiceVolumeValue = 0

    @staticmethod
    def declareORM(Type):
        BaseEntity.declareORM(Type)

        Type.addAction(Type, "MusicVolume", Activate=True, Update=Options._updateMusicVolume)
        Type.addAction(Type, "SoundVolume", Activate=True, Update=Options._updateSoundVolume)
        Type.addAction(Type, "VoiceVolume", Activate=True, Update=Options._updateVoiceVolume)
        Type.addAction(Type, "Mute", Update=Options._updateMute)
        Type.addAction(Type, "Fullscreen", Update=Options._updateFullscreen)
        Type.addAction(Type, "Widescreen", Update=Options._updateWidescreen)
        Type.addAction(Type, "Cursor", Update=Options.__updateCursor)

    def __init__(self):
        super(Options, self).__init__()
        self.onSliderUpObserver = None
        self.Sliders = OptionsManager.getScrollBars()

        self.LanguageSelectEnable = False

        self.soundCheckController = None

    def _onPreparation(self):
        super(Options, self)._onPreparation()
        # sound volume sliders

        self.firstMusicChange = True
        self.firstSoundChange = True
        self.firstVoiceChange = True

        Options.startMusicVolumeValue = Mengine.getCurrentAccountSettingFloat('MusicVolume')
        Options.startSoundVolumeValue = Mengine.getCurrentAccountSettingFloat('SoundVolume')
        Options.startVoiceVolumeValue = Mengine.getCurrentAccountSettingFloat('VoiceVolume')
        self.Sliders['Music'][0] = Options.startMusicVolumeValue
        self.Sliders['Sound'][0] = Options.startSoundVolumeValue
        self.Sliders['Voice'][0] = Options.startVoiceVolumeValue

        Options.s_start_volume_values = [
            Options.startMusicVolumeValue,
            Options.startSoundVolumeValue,
            Options.startVoiceVolumeValue
        ]

        # Check sound volume buttons:
        self.soundCheckController = CheckSoundController(self.object)

        # language select
        self.LanguageSelectEnable = Mengine.getGameParamBool("LanguageSelect", False)

        if not self.LanguageSelectEnable:
            if GroupManager.hasObject(self.object.Group.name, BUTTON_LANGUAGE_SELECT_NAME):
                button = GroupManager.getObject(self.object.Group.name, BUTTON_LANGUAGE_SELECT_NAME)
                button.setEnable(False)

    @staticmethod
    def setStartVolumeValues(music_value, sound_value, voice_value):
        Options.startMusicVolumeValue = music_value
        Options.startSoundVolumeValue = sound_value
        Options.startVoiceVolumeValue = voice_value

    @staticmethod
    def getStartVolumeValues():
        return Options.s_start_volume_values

    def _updateMusicVolume(self, value):
        if self.firstMusicChange is True:
            Mengine.changeCurrentAccountSetting("MusicVolume", unicode(Options.startMusicVolumeValue))
            self.firstMusicChange = False
        else:
            Mengine.changeCurrentAccountSetting("MusicVolume", unicode(value))

        if self.object.hasObject("Demon_Slider_Music") is False:
            return

        Demon_Slider_Music = self.object.getObject("Demon_Slider_Music")
        Demon_Slider_Music.setParam("Current", value)

    def _updateSoundVolume(self, value):
        if self.firstSoundChange is True:
            Mengine.changeCurrentAccountSetting("SoundVolume", unicode(Options.startSoundVolumeValue))
            self.firstSoundChange = False
        else:
            Mengine.changeCurrentAccountSetting("SoundVolume", unicode(value))

        if self.object.hasObject("Demon_Slider_Sound") is False:
            return

        Demon_Slider_Sound = self.object.getObject("Demon_Slider_Sound")
        Demon_Slider_Sound.setParam("Current", value)

    def _updateVoiceVolume(self, value):
        if self.firstVoiceChange is True:
            Mengine.changeCurrentAccountSetting("VoiceVolume", unicode(Options.startVoiceVolumeValue))
            self.firstVoiceChange = False
        else:
            Mengine.changeCurrentAccountSetting("VoiceVolume", unicode(value))

        if self.object.hasObject("Demon_Slider_Voice") is False:
            return

        Demon_Slider_Voice = self.object.getObject("Demon_Slider_Voice")
        Demon_Slider_Voice.setParam("Current", value)

    def _updateMute(self, value):
        if self.object.hasObject("Demon_CheckBox_Mute") is False:
            return

        Demon_CheckBox_Mute = self.object.getObject("Demon_CheckBox_Mute")
        Demon_CheckBox_Mute.setParam("State", value)

    def _updateFullscreen(self, value):
        if self.object.hasObject("Demon_CheckBox_Fullscreen") is False:
            return

        Demon_CheckBox_Fullscreen = self.object.getObject("Demon_CheckBox_Fullscreen")
        Demon_CheckBox_Fullscreen.setParam("State", value)

    def _updateWidescreen(self, value):
        if self.object.hasObject("Demon_CheckBox_WideScreen") is False:
            return

        Demon_CheckBox_WideScreen = self.object.getObject("Demon_CheckBox_WideScreen")
        Demon_CheckBox_WideScreen.setParam("State", value)

    def __updateCursor(self, value):
        if self.object.hasObject("Demon_CheckBox_Arrow") is False:
            return

        Demon_CheckBox_Arrow = self.object.getObject("Demon_CheckBox_Arrow")
        Demon_CheckBox_Arrow.setParam("State", value)

    def setObservers(self):
        def _clickUp(perc, id):
            try:
                self.object.setParam('{}Volume'.format(id), perc)
                self.Sliders[id][1].setParam('Value', perc)
                self.Sliders[id][0] = perc
            except Exception as ex:
                traceback.print_exc()
                pass

        for name, (_, slider) in self.Sliders.iteritems():
            slider.onScrollEnd.addObserver(_clickUp, name)

    def cancel(self):
        self.object.setParam('MusicVolume', Options.startMusicVolumeValue)
        self.object.setParam('SoundVolume', Options.startSoundVolumeValue)
        self.object.setParam('VoiceVolume', Options.startVoiceVolumeValue)

        self.Sliders['Music'][0] = float(Options.startMusicVolumeValue)
        self.Sliders['Sound'][0] = float(Options.startSoundVolumeValue)
        self.Sliders['Voice'][0] = float(Options.startVoiceVolumeValue)

    def _onActivate(self):
        super(Options, self)._onActivate()

        self.setObservers()
        for name, (perc, slider) in self.Sliders.iteritems():
            slider.setParam('Value', perc)

        def __onSliderUp(slider):
            soundSlider = self.object.getObject("Demon_Slider_Sound")
            if slider is soundSlider:
                Notification.notify(Notificator.onSliderUpDing)
                return False
            return False

        self.onSliderUpObserver = Notification.addObserver(Notificator.onSliderUp, __onSliderUp)

        isMobile = Mengine.hasTouchpad()

        # Full screen mode
        if isMobile is True:
            if self.object.hasObject("Demon_CheckBox_Fullscreen") is True:
                Demon_CheckBox_Fullscreen = self.object.getObject("Demon_CheckBox_Fullscreen")
                Demon_CheckBox_Fullscreen.setParam("Enable", False)

        # More options
        if isMobile is True:
            if self.object.getParent().hasObject("Movie2Button_More"):
                moreOptionsButton = self.object.getParent().getObject("Movie2Button_More")
                moreOptionsButton.getEntityNode().removeFromParent()
                moreOptionsButton.onDestroy()
        else:
            with TaskManager.createTaskChain(Name='Menu_Options_MoreOptions', Repeat=True) as tc:
                tc.addTask('TaskMovie2ButtonClick', GroupName="Options", Movie2ButtonName='Movie2Button_More')
                tc.addScope(self.scopeClose, "Options")
                tc.addTask('TaskSceneLayerGroupEnable', LayerName='OptionsMore', Value=True)
                tc.addScope(self.scopeOpen, "OptionsMore")
                tc.addTask('TaskSceneLayerGroupEnable', LayerName='Options', Value=False)

        # Ok
        with TaskManager.createTaskChain(Name='Menu_Options_Ok', GroupName='Options', Repeat=True) as tc:
            tc.addTask('TaskMovie2ButtonClick', Movie2ButtonName='Movie2Button_OK')
            with tc.addParallelTask(2) as (guard_source_movie, guard_source_fade):
                guard_source_movie.addScope(self.scopeClose, "Options")
                guard_source_fade.addTask('AliasFadeOut', FadeGroupName='FadeUI', From=0.5, Time=250.0)
            tc.addTask('TaskNotify', ID=Notificator.OptionsClose)
            tc.addTask('TaskSceneLayerGroupEnable', LayerName='Options', Value=False)

        # Cancel
        with TaskManager.createTaskChain(Name='Menu_Options_Cancel', GroupName='Options', Repeat=True) as Cancel:
            Cancel.addTask('TaskMovie2ButtonClick', Movie2ButtonName='Movie2Button_Cancel')
            Cancel.addFunction(self.cancel)
            with Cancel.addParallelTask(2) as (guard_source_movie, guard_source_fade):
                guard_source_movie.addScope(self.scopeClose, "Options")
                guard_source_fade.addTask('AliasFadeOut', FadeGroupName='FadeUI', From=0.5, Time=250.0)
            Cancel.addTask('TaskNotify', ID=Notificator.OptionsClose)
            Cancel.addTask('TaskSceneLayerGroupEnable', LayerName='Options', Value=False)

        # Socket close
        with TaskManager.createTaskChain(Name='Menu_Options_Click_Out', GroupName='Options', Repeat=True) as Cancel:
            Cancel.addTask('TaskMovie2SocketClick', GroupName="Options", SocketName="close", Movie2Name='Movie2_BG', isDown=True)
            Cancel.addFunction(self.cancel)
            with Cancel.addParallelTask(2) as (guard_source_movie, guard_source_fade):
                guard_source_movie.addScope(self.scopeClose, "Options")
                guard_source_fade.addTask('AliasFadeOut', FadeGroupName='FadeUI', From=0.5, Time=250.0)
            Cancel.addTask('TaskNotify', ID=Notificator.OptionsClose)
            Cancel.addTask('TaskSceneLayerGroupEnable', LayerName='Options', Value=False)

        # Music volume
        if self.object.hasObject("Demon_Slider_Music") is True:
            with TaskManager.createTaskChain(Name="Menu_Options_MusicVolume", Group=self.object, Repeat=True) as tc:
                def __onSliderFilter(slider, value):
                    self.object.setParam("MusicVolume", value)

                    return True

                tc.addTask("TaskFilter", ObjectName="Demon_Slider_Music", ID=Notificator.onSlider, Filter=__onSliderFilter)

        # Sound volume
        if self.object.hasObject("Demon_Slider_Sound") is True:
            with TaskManager.createTaskChain(Name="Menu_Options_SoundVolume", Group=self.object, Repeat=True) as tc:
                def __onSliderFilter(slider, value):
                    self.object.setParam("SoundVolume", value)

                    return True

                tc.addTask("TaskFilter", ObjectName="Demon_Slider_Sound", ID=Notificator.onSlider, Filter=__onSliderFilter)

        # Voice volume
        if self.object.hasObject("Demon_Slider_Voice") is True:
            with TaskManager.createTaskChain(Name="Menu_Options_VoiceVolume", Group=self.object, Repeat=True) as tc:
                def __onSliderFilter(slider, value):
                    self.object.setParam("VoiceVolume", value)

                    return True

                tc.addTask("TaskFilter", ObjectName="Demon_Slider_Voice", ID=Notificator.onSlider, Filter=__onSliderFilter)

        # Mute mode
        if self.object.hasObject("Demon_CheckBox_Mute") is True:
            with TaskManager.createTaskChain(Name="Menu_Options_Mute", Group=self.object, Repeat=True) as tc:
                def __onCheckBoxFilter(checkbox, value):
                    Mengine.changeCurrentAccountSetting("Mute", unicode(value))
                    return True

                tc.addTask("TaskFilter", ObjectName="Demon_CheckBox_Mute", ID=Notificator.onCheckBox, Filter=__onCheckBoxFilter)

        # Disable screen settings in mobile mode
        if isMobile is True:
            DemonNames = ["Demon_CheckBox_Arrow", "Demon_CheckBox_Fullscreen", "Demon_CheckBox_WideScreen"]
            for DemonName in DemonNames:
                if self.object.hasObject(DemonName) is True:
                    Demon = self.object.getObject(DemonName)
                    Demon.setParam("Enable", False)

            TextNames = ["Text_OptionsSystemCursor", "Text_OptionsFullscreen", "Text_OptionsWideScreen"]
            for TextName in TextNames:
                Group = self.object.getGroup()
                if Group.hasObject(TextName) is True:
                    Text = Group.getObject(TextName)
                    Text.setParam("Enable", False)

        else:
            # System cursor
            if self.object.hasObject("Demon_CheckBox_Arrow") is True:
                with TaskManager.createTaskChain(Name="Menu_Options_Arrow", Group=self.object, Repeat=True) as tc:
                    def __onCheckBoxFilter(checkbox, value):
                        Mengine.changeCurrentAccountSetting("Cursor", unicode(value))

                        return True

                    tc.addTask("TaskFilter", ObjectName="Demon_CheckBox_Arrow", ID=Notificator.onCheckBox, Filter=__onCheckBoxFilter)

            if self.object.hasObject("Demon_CheckBox_Fullscreen") is True:
                with TaskManager.createTaskChain(Name="Menu_Options_Fullscreen", Group=self.object, Repeat=True) as tc:
                    def __onCheckBoxFilter(checkbox, value):
                        Mengine.changeCurrentAccountSetting("Fullscreen", unicode(value))

                        return True

                    tc.addTask("TaskFilter", ObjectName="Demon_CheckBox_Fullscreen", ID=Notificator.onCheckBox, Filter=__onCheckBoxFilter)

            # Widescreen
            if self.object.hasObject("Demon_CheckBox_WideScreen") is True:
                with TaskManager.createTaskChain(Name="Menu_Options_WideScreen", Group=self.object, Repeat=True) as tc:
                    def __onCheckBoxFilter(checkbox, value):
                        Mengine.changeCurrentAccountSettingBool("Widescreen", value)

                        return True

                    tc.addTask("TaskFilter", ObjectName="Demon_CheckBox_WideScreen", ID=Notificator.onCheckBox, Filter=__onCheckBoxFilter)

        # Set to default
        if self.object.hasObject("Button_Default"):
            with TaskManager.createTaskChain(Name="Menu_Options_Default", Group=self.object, Repeat=True) as tc:
                tc.addTask("TaskButtonClick", ButtonName="Button_Default")
                tc.addTask("TaskFunction", Fn=self.setDefaultValues)

        elif self.object.hasObject("MovieButton_Default"):
            with TaskManager.createTaskChain(Name="Menu_Options_Default", Group=self.object, Repeat=True) as tc:
                tc.addTask("TaskButtonClick", ButtonName="MovieButton_Default")
                tc.addTask("TaskFunction", Fn=self.setDefaultValues)

        ''' LANGUAGE SELECT OPTIONS BUTTON HANDLE '''
        if self.LanguageSelectEnable:
            if GroupManager.hasObject(self.object.Group.name, BUTTON_LANGUAGE_SELECT_NAME):
                button = GroupManager.getObject(self.object.Group.name, BUTTON_LANGUAGE_SELECT_NAME)

                with TaskManager.createTaskChain(Name="Menu_Options_LanguageSelect", Group=self.object, Repeat=True) as tc:
                    tc.addTask("TaskMovie2ButtonClick", Movie2Button=button)

                    tc.addScope(self.scopeClose, "Options")
                    tc.addTask("TaskSceneLayerGroupEnable", LayerName="LanguageSelect", Value=True)
                    tc.addScope(self.scopeOpen, "LanguageSelect")
                    tc.addTask("TaskSceneLayerGroupEnable", LayerName="Options", Value=False)

            else:
                Trace.log("Entity", 4, "%s has not found %s. Please add to Options.aep, Options.psd if you need." % (
                    self.__class__.__name__, BUTTON_LANGUAGE_SELECT_NAME))

    def scopeOpen(self, source, GropName):
        MovieName = "Movie2_Open"
        source.addScope(self.SceneEffect, GropName, MovieName)

    def scopeClose(self, source, GropName):
        MovieName = "Movie2_Close"
        source.addScope(self.SceneEffect, GropName, MovieName)

    def SceneEffect(self, source, GropName, MovieName):
        if GroupManager.hasObject(GropName, MovieName) is True:
            Movie = GroupManager.getObject(GropName, MovieName)
            with GuardBlockInput(source) as guard_source:
                with guard_source.addParallelTask(2) as (guard_source_movie, guard_source_fade):
                    guard_source_movie.addTask("TaskEnable", Object=Movie, Value=True)
                    guard_source_movie.addTask("TaskMovie2Play", Movie2=Movie, Wait=True)
                    guard_source_movie.addTask("TaskEnable", Object=Movie, Value=False)

    def setDefaultValues(self):
        musicValue = DefaultManager.getDefaultFloat("DefaultMusicVolume", 0.5)
        Mengine.changeCurrentAccountSetting("MusicVolume", unicode(musicValue))

        soundValue = DefaultManager.getDefaultFloat("DefaultSoundVolume", 0.5)
        Mengine.changeCurrentAccountSetting("SoundVolume", unicode(soundValue))

        voiceValue = DefaultManager.getDefaultFloat("DefaultVoiceVolume", 0.5)
        Mengine.changeCurrentAccountSetting("VoiceVolume", unicode(voiceValue))

        muteValue = DefaultManager.getDefaultBool("DefaultMute", False)
        Mengine.changeCurrentAccountSettingBool("Mute", muteValue)
        self.object.setParam("Mute", muteValue)

        fullscreenValue = DefaultManager.getDefaultBool("DefaultFullscreen", True)
        Mengine.changeCurrentAccountSetting("Fullscreen", unicode(fullscreenValue))
        self.object.setParam("Fullscreen", fullscreenValue)

        widescreenValue = DefaultManager.getDefaultBool("DefaultWidescreen", False)
        Mengine.changeCurrentAccountSettingBool("Widescreen", widescreenValue)
        self.object.setParam("Widescreen", widescreenValue)

        cursorValue = DefaultManager.getDefaultBool("DefaultCursor", False)
        Mengine.changeCurrentAccountSetting("Cursor", unicode(cursorValue))
        self.object.setParam("Cursor", cursorValue)

    def _onDeactivate(self):
        super(Options, self)._onDeactivate()

        if self.soundCheckController is not None:
            self.soundCheckController.cleanUp()
            self.soundCheckController = None

        Notification.removeObserver(self.onSliderUpObserver)
        self.onSliderUpObserver = None

        for _, slider in self.Sliders.values():
            slider.onScrollEnd.removeObservers()

        if TaskManager.existTaskChain("Menu_Options_MusicVolume"):
            TaskManager.cancelTaskChain("Menu_Options_MusicVolume")

        if TaskManager.existTaskChain("Menu_Options_SoundVolume"):
            TaskManager.cancelTaskChain("Menu_Options_SoundVolume")

        if TaskManager.existTaskChain("Menu_Options_Mute"):
            TaskManager.cancelTaskChain("Menu_Options_Mute")

        if TaskManager.existTaskChain("Menu_Options_Arrow"):
            TaskManager.cancelTaskChain("Menu_Options_Arrow")

        if TaskManager.existTaskChain("Menu_Options_VoiceVolume"):
            TaskManager.cancelTaskChain("Menu_Options_VoiceVolume")

        if TaskManager.existTaskChain("Menu_Options_WideScreen"):
            TaskManager.cancelTaskChain("Menu_Options_WideScreen")

        if TaskManager.existTaskChain("Menu_Options_Default"):
            TaskManager.cancelTaskChain("Menu_Options_Default")

        if TaskManager.existTaskChain("Menu_Options_Fullscreen"):
            TaskManager.cancelTaskChain("Menu_Options_Fullscreen")

        if TaskManager.existTaskChain("Menu_Options_MoreOptions"):
            TaskManager.cancelTaskChain("Menu_Options_MoreOptions")

        if TaskManager.existTaskChain("Menu_Options_About"):
            TaskManager.cancelTaskChain("Menu_Options_About")

        if TaskManager.existTaskChain("Menu_Options_Ok"):
            TaskManager.cancelTaskChain("Menu_Options_Ok")

        if TaskManager.existTaskChain("Menu_Options_Cancel"):
            TaskManager.cancelTaskChain("Menu_Options_Cancel")

        if TaskManager.existTaskChain("Menu_Options_Click_Out"):
            TaskManager.cancelTaskChain("Menu_Options_Click_Out")

        if TaskManager.existTaskChain("Menu_Options_LanguageSelect"):
            TaskManager.cancelTaskChain("Menu_Options_LanguageSelect")
