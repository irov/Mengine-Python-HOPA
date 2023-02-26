from Foundation.DefaultManager import DefaultManager
from Foundation.DemonManager import DemonManager
from Foundation.GuardBlockInput import GuardBlockInput
from Foundation.SceneManager import SceneManager
from Foundation.System import System
from Foundation.Utils import isCollectorEdition
from HOPA.BonusManager import BonusManager
from HOPA.BonusVideoManager import BonusVideoManager
from HOPA.TransitionManager import TransitionManager
from HOPA.WallPaperManager import WallPaperManager
from HOPA.ZoomManager import ZoomManager

class SystemBonus(System):
    def _onParams(self, params):
        super(SystemBonus, self)._onParams(params)
        self.current_state = None
        self.demons_change_buttons = BonusManager.getStates()
        self.current_scene = None
        self.current_game_scene = None

    def _onRun(self):
        if isCollectorEdition() is False:
            return True

        self.__restoreDefaultManagerParams()

        self.addObserver(Notificator.onBonusSceneChangeState, self.__cbChangeState)
        self.addObserver(Notificator.onBonusSceneTransition, self.__cbTransitionTo)
        self.addObserver(Notificator.onTransitionBegin, self.__cbSetTransitionStatus)
        self.addObserver(Notificator.onBonusCutScenePlay, self.__cbCutScenePlay)
        self.addObserver(Notificator.onBonusVideoOpenCutScene, self.__cbBonusVideoOpenCutScene)

        self.__runTaskChains()

        return True

    def __runTaskChains(self):
        if isCollectorEdition() is False:
            return

        with self.createTaskChain(Name="BonusScene", GroupName="Bonus", Global=True, Repeat=True) as tc:
            with tc.addRaceTask(2) as (source_switch_state, source_transition):
                for state, source_state_click in source_switch_state.addRaceTaskList(BonusManager.getStates().values()):
                    source_state_click.addTask("TaskMovie2ButtonClick", Movie2ButtonName=state.button_name)

                    source_state_click.addNotify(Notificator.onBonusSceneChangeState, state.state_id)

                for transition, source_transition_click in source_transition.addRaceTaskList(BonusManager.getTransitions().values()):
                    source_transition_click.addTask("TaskMovie2ButtonClick", Movie2ButtonName=transition.transition_button)
                    source_transition_click.addScope(self._scopeTransition, transition.scene_to)

    def _scopeTransition(self, source, scene_to):
        source.addNotify(Notificator.onBonusSceneTransition, scene_to)

    def __cbBonusVideoOpenCutScene(self, page_id):
        videos = BonusVideoManager.getVideos()
        video = videos.get(page_id)

        if video is None:
            return False

        if video.isReceived is True:
            return False

        video.isReceived = True

        BonusVideoManager.incCounterReceivedVideos()
        return False

    def _onStop(self):
        pass

    def __cbSetTransitionStatus(self, scene_from=None, scene_to=None, zoom_name=None):
        if scene_to is None or scene_to != 'Bonus':
            return False

        states = BonusManager.getStates()
        for state in states.values():
            if state.status is True:
                self.current_state = state.state_id
            demon = DemonManager.getDemon(state.demon_name)
            demon.setEnable(state.status)

        return False

    def __cbChangeState(self, state_name):
        current_state = self.demons_change_buttons.get(self.current_state)
        new_state = self.demons_change_buttons.get(state_name)

        current_state_demon = DemonManager.getDemon(current_state.demon_name)
        new_state_demon = DemonManager.getDemon(new_state.demon_name)

        current_state.status = False
        new_state.status = True

        self.__changeStateAnimation(current_state_demon, new_state_demon)
        self.current_state = state_name

        return False

    def __changeStateAnimation(self, current_demon, new_demon):
        animation_time = DefaultManager.getDefaultFloat("BonusSceneChangeStateTime", 1000.0)

        if self.existTaskChain('ChangeStateAnimation'):
            self.removeTaskChain('ChangeStateAnimation')

        with self.createTaskChain(Name='ChangeStateAnimation') as tc:
            with GuardBlockInput(tc) as guard_source:
                with guard_source.addParallelTask(2) as (current_state_source, new_state_source):
                    current_state_source.addTask("AliasObjectAlphaTo", Object=current_demon, Time=animation_time, From=1.0, To=0.0)
                    current_state_source.addDisable(current_demon)

                    new_state_source.addEnable(new_demon)
                    new_state_source.addTask("AliasObjectAlphaTo", Object=new_demon, Time=animation_time, From=0.0, To=1.0)

    def __cbTransitionTo(self, scene_name):
        if scene_name is None:
            return False

        current_scene_name = SceneManager.getCurrentSceneName()
        if current_scene_name == "Store":
            current_scene_name = SceneManager.getPrevSceneName()

        if DemonManager.hasDemon(scene_name):
            demon = DemonManager.getDemon(scene_name)
            demon.setParam("PreviousSceneName", current_scene_name)

        open_zoom = ZoomManager.getZoomOpenGroupName()
        if open_zoom is not None:
            # if we don't close zoom, then in search mode this zoom will be open -> bugs
            # https://wonderland-games.atlassian.net/browse/CAME2-1314
            ZoomManager.closeZoom(open_zoom)

        TransitionManager.changeScene(scene_name)
        return False

    def __cbCutScenePlay(self, cut_scene_name):
        if self.existTaskChain('CutScenePlay'):
            self.removeTaskChain('CutScenePlay')

        with self.createTaskChain(Name='CutScenePlay') as tc:
            tc.addFunction(self.curentSceneSave)
            tc.addScope(self._scopePlay, cut_scene_name)

        return False

    def _scopePlay(self, source, cut_scene_name):
        source.addTask("TaskCutScenePlay", CutSceneName=cut_scene_name, Transition=True)
        source.addTask("AliasTransition", SceneName=self.current_scene)
        source.addFunction(self.curentSceneDone)

    def curentSceneSave(self):
        self.current_scene = SceneManager.getCurrentSceneName()
        self.current_game_scene = SceneManager.getCurrentGameSceneName()

    def curentSceneDone(self):
        self.current_scene = None
        SceneManager.setCurrentGameSceneName(self.current_game_scene)
        self.current_game_scene = None

    @staticmethod
    def __restoreDefaultManagerParams():
        # WallpapersManager
        wallpaper_params = WallPaperManager.getWallpapers()
        wallpaper_default_status = WallPaperManager.getWallpapersDefaultStatus()
        for param in wallpaper_params:
            index = wallpaper_params.index(param)
            wallpaper_params[index].status = wallpaper_default_status[index]

        # BonusVideoManager
        bonus_video_params = BonusVideoManager.getVideos()
        bonus_video_recieved_counter = BonusVideoManager.getCounterReceivedVideos()
        for param in bonus_video_params.values():
            param.isReceived = False
        bonus_video_recieved_counter = 0

        # BonusManager
        bonus_params = BonusManager.getStates()
        bonus_default_status = BonusManager.getStatesDefaultStatus()
        for state_id, state_param in bonus_params.items():
            state_param.status = bonus_default_status[state_id]

    @staticmethod
    def _onSave():
        wallpaper_manager_data = dict()
        bonus_video_data = dict()
        bonus_manager_data = dict()

        save_data = {'WallpaperManagerData': wallpaper_manager_data, 'BonusVideoManagerData': bonus_video_data, 'BonusManagerData': bonus_manager_data}

        # wallpaper_manager_data:
        wallpapers = WallPaperManager.getWallpapers()
        for wallpaper in wallpapers:
            wallpaper_manager_data[wallpaper.wp_id] = wallpaper.status

        # bonus_video_data
        videos_received_statuses = dict()
        videos = BonusVideoManager.getVideos()
        for video_id, video in videos.items():
            videos_received_statuses[video_id] = video.isReceived

        bonus_video_data['VideoReceivedStatuses'] = videos_received_statuses
        bonus_video_data['CounterReceivedStates'] = BonusVideoManager.getCounterReceivedVideos()

        # bonus_manager_data
        states = BonusManager.getStates()
        for state_id, state in states.items():
            bonus_manager_data[state_id] = state.status

        return save_data

    @staticmethod
    def _onLoad(save_data):
        wallpaper_manager_data = save_data.get('WallpaperManagerData', {})
        bonus_video_data = save_data.get('BonusVideoManagerData', {})
        bonus_manager_data = save_data.get('BonusManagerData', {})

        # wallpaper_manager_data:
        for wp_id, status in wallpaper_manager_data.items():
            wallpaper = WallPaperManager.getWallpaperById(wp_id)
            wallpaper.status = status

        # bonus_video_data
        videos_received_statuses = bonus_video_data.get('VideoReceivedStatuses', {})
        for video_id, video_received_status in videos_received_statuses.items():
            video = BonusVideoManager.getVideo(video_id)
            video.isReceived = video_received_status

        BonusVideoManager.s_counter_received_videos = bonus_video_data.get('CounterReceivedStates', 0)

        # bonus_manager_data
        for state_id, state_status in bonus_manager_data.items():
            state = BonusManager.getState(state_id)
            state.status = state_status