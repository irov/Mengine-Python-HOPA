from Foundation.GroupManager import GroupManager
from Foundation.GuardBlockInput import GuardBlockInput
from Foundation.System import System
from HOPA.TransitionManager import TransitionManager
from Notification import Notification


SCENE_EFFECT_MOVIE_OPEN = "Movie2_Open"
SCENE_EFFECT_MOVIE_CLOSE = "Movie2_Close"


class SystemInGameMenuCall(System):
    def __init__(self):
        super(SystemInGameMenuCall, self).__init__()
        self.MenuFade = 0.5

    def _onParams(self, params):
        super(SystemInGameMenuCall, self)._onParams(params)
        self.onKeyEventObserver = None
        self.onGameStageEnterObserver = None
        self.onGameStageLeaveObserver = None

    def _onRun(self):
        self.addObserver(Notificator.onKeyEvent, self.__onKeyEvent)
        self.__runTaskChain()
        return True

    def __scopeOpen(self, source, group_name, ingame_menu_first_open=False):
        source.addScope(self.__scopeSceneEffect, group_name, SCENE_EFFECT_MOVIE_OPEN)
        if group_name is "InGameMenu" and ingame_menu_first_open is True:
            source.addNotify(Notificator.onInGameMenuShow, True)
            source.addNotify(Notificator.onMacroArrowAttach, False)

    def __scopeClose(self, source, group_name, ingame_menu_full_close=False):
        source.addScope(self.__scopeSceneEffect, group_name, SCENE_EFFECT_MOVIE_CLOSE)
        if group_name is "InGameMenu" and ingame_menu_full_close is True:
            source.addNotify(Notificator.onInGameMenuShow, False)
            source.addNotify(Notificator.onMacroArrowAttach, True)

    def __scopeSceneEffect(self, source, group_name, movie_name):
        if not GroupManager.hasObject(group_name, movie_name):
            return
        scene_effect_movie = GroupManager.getObject(group_name, movie_name)
        with GuardBlockInput(source) as guard_source:
            with guard_source.addParallelTask(2) as (guard_source_movie, guard_source_fade):
                guard_source_movie.addTask("TaskEnable", Object=scene_effect_movie, Value=True)
                guard_source_movie.addTask("TaskMovie2Play", Movie2=scene_effect_movie, Wait=True)
                guard_source_movie.addTask("TaskEnable", Object=scene_effect_movie, Value=False)

    def __runTaskChain(self):
        movie2_button_menu = GroupManager.getObject("Toolbar", "Movie2Button_Menu")

        with self.createTaskChain(Name="Toolbar_Menu", Global=True, Repeat=True) as tc:
            tc.addTask("TaskMovie2ButtonClick", Movie2Button=movie2_button_menu)
            tc.addFunction(movie2_button_menu.setBlock, True)
            tc.addTask("TaskSceneLayerGroupEnable", LayerName="InGameMenu", Value=True)
            with tc.addParallelTask(2) as (guard_source_movie, guard_source_fade):
                guard_source_movie.addScope(self.__scopeOpen, "InGameMenu", True)
                guard_source_fade.addTask("AliasFadeIn", FadeGroupName="FadeUI", To=self.MenuFade, Time=250.0)

        with self.createTaskChain(Name="InGameMenu", Global=True, Repeat=True) as tc:
            with tc.addRepeatTask() as (tc_repeat, tc_until):
                tc_repeat.addScope(self._scopeMenuButtons)

                with tc_until.addRaceTask(4) as (tc_resume, tc_quit, tc_skip, tc_click_out_resume):
                    tc_skip.addListener(Notificator.onSceneDeactivate)
                    tc_skip.addFunction(movie2_button_menu.setBlock, False)

                    tc_click_out_resume.addScope(self._scopeResumeMenuOutClick, movie2_button_menu)
                    tc_resume.addScope(self._scopeResume, movie2_button_menu)
                    tc_quit.addScope(self._scopeQuit, movie2_button_menu)

    # ---- InGameMenu methods ------------------------------------------------------------------------------------------

    def _scopeMenuButtons(self, source):
        with source.addRaceTask(2) as (tc_options, tc_difficulty):
            tc_options.addTask("TaskMovie2ButtonClick", GroupName='InGameMenu', Movie2ButtonName="Movie2Button_Options")
            tc_options.addScope(self.__scopeClose, "InGameMenu")
            tc_options.addTask("TaskSceneLayerGroupEnable", LayerName="InGameMenu", Value=False)
            tc_options.addTask("TaskSceneLayerGroupEnable", LayerName="Options", Value=True)
            tc_options.addScope(self.__scopeOpen, "Options")
            tc_options.addTask('TaskListener', ID=Notificator.OptionsClose)
            tc_options.addTask('TaskSceneLayerGroupEnable', LayerName='InGameMenu', Value=True)
            tc_options.addTask("AliasFadeIn", FadeGroupName="FadeUI", Time=250.0, To=self.MenuFade)
            tc_options.addScope(self.__scopeOpen, "InGameMenu")

            tc_difficulty.addTask('TaskMovie2ButtonClick', GroupName='InGameMenu',
                                  Movie2ButtonName='Movie2Button_Difficulty')
            tc_difficulty.addScope(self.__scopeClose, "InGameMenu")
            tc_difficulty.addTask('TaskSceneLayerGroupEnable', LayerName='InGameMenu', Value=False)
            tc_difficulty.addTask('TaskSceneLayerGroupEnable', LayerName='Difficulty', Value=True)
            tc_difficulty.addScope(self.__scopeOpen, "Difficulty")
            tc_difficulty.addTask('TaskListener', ID=Notificator.onSelectedDifficulty)
            tc_difficulty.addTask('TaskSceneLayerGroupEnable', LayerName='InGameMenu', Value=True)
            tc_difficulty.addScope(self.__scopeOpen, "InGameMenu")

    def _scopeResume(self, source, movie2_button_menu):
        source.addTask("TaskMovie2ButtonClick", GroupName='InGameMenu', Movie2ButtonName="Movie2Button_Continue")

        with GuardBlockInput(source) as guard_tc_resume:
            guard_tc_resume.addFunction(movie2_button_menu.setBlock, False)
            with guard_tc_resume.addParallelTask(2) as (guard_source_movie, guard_source_fade):
                guard_source_movie.addScope(self.__scopeClose, "InGameMenu", True)
                guard_source_fade.addTask("AliasFadeOut", FadeGroupName="FadeUI", From=self.MenuFade, Time=250.0)
            guard_tc_resume.addTask("TaskSceneLayerGroupEnable", LayerName="InGameMenu", Value=False)

    def _scopeResumeMenuOutClick(self, source, movie2_button_menu):
        source.addTask("TaskMovie2SocketClick", GroupName="InGameMenu", Movie2Name="Movie2_BG", SocketName="close",
                       isDown=True)

        with GuardBlockInput(source) as guard_tc_resume:
            guard_tc_resume.addFunction(movie2_button_menu.setBlock, False)
            with guard_tc_resume.addParallelTask(2) as (guard_source_movie, guard_source_fade):
                guard_source_movie.addScope(self.__scopeClose, "InGameMenu", True)
                guard_source_fade.addTask("AliasFadeOut", FadeGroupName="FadeUI", From=self.MenuFade, Time=250.0)
            guard_tc_resume.addTask("TaskSceneLayerGroupEnable", LayerName="InGameMenu", Value=False)

    def _scopeQuit(self, source, movie2_button_menu):
        source.addTask("TaskMovie2ButtonClick", GroupName='InGameMenu', Movie2ButtonName="Movie2Button_Exit")
        with GuardBlockInput(source) as guard_tc_quit:
            guard_tc_quit.addScope(self.__scopeClose, "InGameMenu")
            guard_tc_quit.addTask("TaskSceneLayerGroupEnable", LayerName="InGameMenu", Value=False)
            guard_tc_quit.addTask("AliasMessageShow", TextID="ID_POPUP_CONFIRM_QUIT")

        with source.addRaceTask(2) as (tc_no, tc_yes):
            tc_no.addTask("AliasMessageNo")
            with tc_no.addParallelTask(2) as (tc_no_1, tc_no_2):
                tc_no_1.addTask("AliasMessageHide")
                # tc_no_1.addFunction(movie2_button_menu.setBlock, False)
                tc_no_2.addTask("AliasFadeOut", FadeGroupName="FadeUI", Time=250.0, From=self.MenuFade)
                tc_no_2.addTask("AliasFadeIn", FadeGroupName="FadeUI", Time=250.0, To=self.MenuFade)
                tc_no_2.addTask('TaskSceneLayerGroupEnable', LayerName='InGameMenu', Value=True)
                tc_no_2.addScope(self.__scopeOpen, "InGameMenu")

            tc_yes.addTask("AliasMessageYes")
            with tc_yes.addParallelTask(2) as (tc_yes_1, tc_yes_2):
                tc_yes_1.addTask("AliasMessageHide")
                tc_yes_1.addFunction(movie2_button_menu.setBlock, False)
                tc_yes_2.addTask("AliasFadeOut", FadeGroupName="FadeUI", Time=250.0, From=self.MenuFade)
                tc_yes_2.addFunction(movie2_button_menu.setBlock, False)
                tc_yes_2.addNotify(Notificator.onMusicPlatlistPlay, "Playlist_Menu")

            # tc_yes.addTask("AliasTransition", SceneName="Menu")
            tc_yes.addFunction(TransitionManager.changeScene, "Menu")

    # ------------------------------------------------------------------------------------------ InGameMenu methods ----

    def __onKeyEvent(self, key, x, y, isDown, isRepeating):
        if isDown != 1:
            return False

        if key == Mengine.KC_ESCAPE:
            Notification.notify(Notificator.onInGameMenuCalled)
        return False
