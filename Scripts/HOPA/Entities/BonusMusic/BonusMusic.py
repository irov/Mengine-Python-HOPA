from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.GroupManager import GroupManager
from Foundation.GuardBlockInput import GuardBlockInput
from Foundation.TaskManager import TaskManager
from HOPA.BonusManager import BonusManager
from HOPA.BonusMusicManager import BonusMusicManager
from HOPA.MusicManager import MusicManager

from MusicPlate import MusicPlate

class BonusMusic(BaseEntity):
    def __init__(self):
        super(BonusMusic, self).__init__()
        self.music_plates = {}
        self.bg = None
        self.current_plate = None

        self.b_is_music_button_active = False

    def _onPreparation(self):
        switch_buttons = BonusManager.getStates()
        for button in switch_buttons.values():
            GroupManager.getObject('Bonus', button.button_name).setBlock(False)

        button_music = GroupManager.getObject('Bonus', 'Movie2Button_BonusMusic')
        button_music.setBlock(True)

        self.object_entity_node = self.object.getEntityNode()

        self.bg = self.object.getObject('Movie2_MusicBG')

        self.save_music = self.object.getObject('Movie2Button_SaveMusic')
        self.save_music.setBlock(True)

        if self.object.hasObject('Movie2Scrollbar_Volume'):
            self.scrollbar_volume = self.object.getObject('Movie2Scrollbar_Volume')
            music_volume = Mengine.getCurrentAccountSettingFloat("MusicVolume")
            self.scrollbar_volume.setValue(music_volume)

        for music_param in BonusMusicManager.getBonusMusic().values():
            plate = self.__createPlate(music_param)
            self.music_plates[music_param.music_id] = plate

        self.popup_save_music = self.object.getObject('Movie2_PlatePopupMusicSave')
        self.popup_save_music_button_yes = self.object.getObject('Movie2Button_PopupMusicSaveYes')
        self.popup_save_music_button_cancel = self.object.getObject('Movie2Button_PopupMusicSaveCancel')
        self.popup_save_music_entity_node = self.popup_save_music.getEntityNode()

        if self.object.hasObject('Movie2_SceneEffectOpen'):
            self.scene_effect_open_popup_save_music = self.object.getObject('Movie2_SceneEffectOpen')

        if self.object.hasObject('Movie2_SceneEffectClose'):
            self.scene_effect_close_popup_save_music = self.object.getObject('Movie2_SceneEffectClose')

        popup_save_music_slot_yes = self.popup_save_music.getMovieSlot('button_yes')
        popup_save_music_slot_cancel = self.popup_save_music.getMovieSlot('button_cancel')

        popup_save_music_slot_yes.addChild(self.popup_save_music_button_yes.getEntityNode())
        popup_save_music_slot_cancel.addChild(self.popup_save_music_button_cancel.getEntityNode())

        self.popup_save_music.setEnable(False)

    def _onActivate(self):
        if self.scrollbar_volume is not None:
            self.setScrollbarObserver()
        self._runTaskChain()

    def _onDeactivate(self):
        # def dropMusic(*_):
        #     Notification.notify(Notificator.onBonusMusicPlaylistPlay, None)
        #     return True
        #
        # Notification.addObserver(Notificator.onSceneLeave, dropMusic)

        if self.b_is_music_button_active:  # Drop ambient music only if it was changed
            Notification.notify(Notificator.onBonusMusicPlaylistPlay, None)
            self.b_is_music_button_active = False

        self.__cleanUp()

    def __setCurrentPlate(self, plate):
        self.current_plate = plate

    def __createPlate(self, music_param):
        plate_id = music_param.music_id
        slot_id = music_param.slot_id

        movie_plate_name = 'PlateMusic{}'.format(plate_id)
        button_play_on_name = 'PlayMusicButtonOn{}'.format(plate_id)
        button_play_off_name = 'PlayMusicButtonOff{}'.format(plate_id)

        movie_plate = self.object.tryGenerateObjectUnique(movie_plate_name, 'Movie2_MusicPlate', Enable=True)
        button_play_on = self.object.tryGenerateObjectUnique(button_play_on_name, 'Movie2Button_MusicOn')
        button_play_off = self.object.tryGenerateObjectUnique(button_play_off_name, 'Movie2Button_MusicOff')

        plate_slot = self.bg.getMovieSlot(slot_id)
        plate_slot.addChild(movie_plate.getEntityNode())

        button_slot = movie_plate.getMovieSlot('button_play')
        button_slot.addChild(button_play_on.getEntityNode())
        button_slot.addChild(button_play_off.getEntityNode())

        plate = MusicPlate(plate_id, music_param, movie_plate, button_play_on, button_play_off)
        return plate

    def _runTaskChain(self):
        self.tc_play_music = TaskManager.createTaskChain(Repeat=True)
        self.tc_save_music = TaskManager.createTaskChain(Repeat=True)

        with self.tc_play_music as tc_play_music:
            for plate, race_click in tc_play_music.addRaceTaskList(self.music_plates.values()):
                with race_click.addRaceTask(2) as (race_click_play_on, race_click_play_off):
                    race_click_play_on.addScope(plate.scopeButtonOnClick)
                    race_click_play_on.addScope(self.__scopeClickPlayOnMusic, plate)

                    race_click_play_off.addScope(plate.scopeButtonOffClick)
                    race_click_play_off.addScope(self.__scopeClickPlayOffMusic, plate)

        with self.tc_save_music as tc_download_music:
            tc_download_music.addTask('TaskMovie2ButtonClick', Movie2Button=self.save_music)
            tc_download_music.addScope(self.__sourceEnableSaveMusicPopup)

    def __scopeClickPlayOnMusic(self, source, new_plate):
        self.b_is_music_button_active = True

        source.addFunction(self.save_music.setBlock, False)

        for plate in self.music_plates.values():
            source.addFunction(plate.setPlay, False)

        source.addNotify(Notificator.onBonusMusicPlaylistPlay, new_plate.music_param.playlist_id)

        source.addFunction(new_plate.setPlay, True)

        source.addFunction(self.__setCurrentPlate, new_plate)

    def __scopeClickPlayOffMusic(self, source, plate):
        self.b_is_music_button_active = False

        source.addFunction(self.save_music.setBlock, True)
        source.addFunction(self.current_plate.setPlay, None)
        source.addFunction(plate.setPlay, False)
        source.addNotify(Notificator.onBonusMusicPlaylistPlay, None)

    def __scopeSavePopupSceneEffect(self, source, open_flag):
        """ Scene effect for open/close popup SaveMusic
        :param source:
        :param open_flag: if True popup SaveMusic will open. If False will close
        :return:
        """
        scene_effect_movie = self.scene_effect_open_popup_save_music if open_flag is True else self.scene_effect_close_popup_save_music

        if scene_effect_movie is None:
            source.addDummy()
            return

        scene_effect_movie_slot = scene_effect_movie.getMovieSlot('scene_effect')

        with GuardBlockInput(source) as guard_source:
            guard_source.addFunction(scene_effect_movie_slot.addChild, self.popup_save_music_entity_node)
            guard_source.addPlay(scene_effect_movie)
            guard_source.addFunction(self.popup_save_music_entity_node.removeFromParent)
            guard_source.addFunction(self.object_entity_node.addChild, self.popup_save_music_entity_node)

    def __sourceEnableSaveMusicPopup(self, source):
        if self.current_plate is None:
            return False

        source.addEnable(self.popup_save_music)
        source.addScope(self.__scopeSavePopupSceneEffect, True)

        with source.addRaceTask(2) as (source_yes, source_cancel):
            source_yes.addTask('TaskMovie2ButtonClick', Movie2Button=self.popup_save_music_button_yes)
            source_yes.addScope(self.__scopeSaveButtonClick)
            source_cancel.addTask('TaskMovie2ButtonClick', Movie2Button=self.popup_save_music_button_cancel)

        source.addScope(self.__scopeSavePopupSceneEffect, False)
        source.addDisable(self.popup_save_music)

    def __scopeSaveButtonClick(self, source):
        """ This method save current music to dir User/Public/Music/*ProjectName*
        :param source:
        :return:
        """

        playlist = MusicManager.getMusicPlaylists().get(self.current_plate.music_param.playlist_id, None)

        if playlist is None:
            return

        _, music_resource = playlist[0]

        source.addFunction(Mengine.copyUserMusic, self.current_plate.music_param.resource_name, r'{}.mp3'.format(self.current_plate.plate_id))

    def setScrollbarObserver(self):
        def _clickUp(perc):
            Mengine.changeCurrentAccountSetting("MusicVolume", unicode(perc))

        self.scrollbar_volume.onScroll.addObserver(_clickUp)

    def __cleanUp(self):
        if self.tc_play_music:
            self.tc_play_music.cancel()
        self.tc_play_music = None

        if self.tc_save_music:
            self.tc_save_music.cancel()
        self.tc_save_music = None

        for plate in self.music_plates.values():
            plate.cleanUp()