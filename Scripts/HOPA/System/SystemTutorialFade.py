from Foundation.System import System
from HOPA.TutorialFadesManager import TutorialFadesManager
from Foundation.GroupManager import GroupManager
from Foundation.TaskManager import TaskManager
from Foundation.GuardBlockInput import GuardBlockInput
from Foundation.SceneManager import SceneManager


class SystemTutorialFade(System):
    is_working = False
    is_enabled = False

    def __init__(self):
        super(SystemTutorialFade, self).__init__()
        # Manager params
        self.fades = {}
        self.config = {}

        # Config param variables
        self.show_hide_group = None
        self.fade_group = None
        self.window_group = None
        self.skip_group = None

        self.fade_slot = None
        self.window_slot = None
        self.skip_slot = None

        self.window_alias = None

        self.skip_button_name = None

        # Other variables
        self.movie_show = None
        self.movie_hide = None
        self.fade_id = None
        self.is_skipped = False
        self.current_scene = None

    def _onRun(self):
        # Fill global variables
        self.fades = TutorialFadesManager.getFades().getParams()
        self.config = TutorialFadesManager.getConfig()

        self.show_hide_group = self.config.get("ShowHideGroup", "FadeTutorial")
        self.fade_group = self.config.get("FadeGroup", "FadeTutorial")
        self.window_group = self.config.get("WindowGroup", None)
        self.skip_group = self.config.get("SkipGroup", "SkipTutorial")

        self.fade_slot = self.config.get("FadeSlot", None)
        self.window_slot = self.config.get("WindowSlot", None)
        self.skip_slot = self.config.get("SkipSlot", "slot")

        self.window_alias = self.config.get("WindowAlias", None)

        self.skip_button_name = self.config.get("SkipButton", "Movie2Button_Skip")

        # Set observers
        self.__setObservers()

        return True

    def __setObservers(self):
        self.addObserver(Notificator.onTutorialFadeShow, self.__cbTutorialFadeShow)
        self.addObserver(Notificator.onTutorialFadeHide, self.__cbTutorialFadeHide)
        self.addObserver(Notificator.onTutorialComplete, self.__cbTutorialComplete)
        self.addObserver(Notificator.onSelectedDifficulty, self.__cbSelectedDifficulty)
        self.addObserver(Notificator.onTutorialSkipEnd, self.__cbTutorialSkip)
        self.addObserver(Notificator.onTransitionEnd, self.__cbTransitionEnd)
        self.addObserver(Notificator.onSceneActivate, self._reloadFade)
        self.addObserver(Notificator.onSceneDeactivate, self.cleanUp)
        self.addObserver(Notificator.onTutorialBlockScreen, self.notifySpicke)

    def __cbTutorialComplete(self):
        TutorialFadesManager.completeTutorial()
        TutorialFadesManager.setActiveTutorialState(False)

        return False

    def __cbSelectedDifficulty(self):
        if TutorialFadesManager.isTutorialComplete():
            return False

        difficulty_tutorial_value = Mengine.getCurrentAccountSettingBool("DifficultyCustomTutorial")
        TutorialFadesManager.setActiveTutorialState(difficulty_tutorial_value)

        return False

    def __cbTutorialSkip(self, some_args=None, some_other_args=None):
        self.cleanUp()
        self.is_skipped = True

        TutorialFadesManager.setActiveTutorialState(False)
        SystemTutorialFade.setWorking(False)
        SystemTutorialFade.setEnabled(False)

        return False

    def __cbTransitionEnd(self, sceneFrom, sceneTo, zoomName):
        if self.is_enabled is True:
            SystemTutorialFade.setWorking(True)
            self.current_scene = sceneTo
            self._reloadFade()
        else:
            SystemTutorialFade.setWorking(False)
            self.current_scene = None

        return False

    def _reloadFade(self, some_args=None, some_other_args=None):
        if self.is_skipped:
            return False

        if self.is_working:
            current_scene_name = SceneManager.getCurrentSceneName()
            if current_scene_name is not None:
                if current_scene_name == self.current_scene:
                    slot = SceneManager.getSceneDescription(current_scene_name)
                    if slot.hasSlotsGroup(self.fade_group):
                        self.__cbTutorialFadeShow(self.fade_id)
                else:
                    self.cleanUp()
        else:
            self.cleanUp()

        return False

    def cleanUp(self, some_args=None, some_other_args=None):
        """
        Disable and return to parent objects for every fade record in fades
        """

        if self.is_skipped:
            return False

        for fade_id in self.fades:
            show, hide, fade, window, window_text, skip = self.getFadeObjects(fade_id)

            if show is not None:
                show.setEnable(False)

            if hide is not None:
                hide.setEnable(False)

            if fade is not None:
                fade.setEnable(False)
                fade.returnToParent()

            if window is not None:
                window.setEnable(False)
                window.returnToParent()

            if skip is not None:
                skip.setEnable(False)
                skip.returnToParent()

        return False

    def getFadeObjects(self, fade_id):
        """
        Get objects variables (default=None) from fade data by custom fade id
        """

        if fade_id not in self.fades:
            return

        fade_data = self.fades.get(fade_id)

        show = None
        show_name = fade_data.get("showName", None)
        if show_name is not None and self.show_hide_group is not None:
            show = GroupManager.getObject(self.show_hide_group, show_name)

        hide = None
        hide_name = fade_data.get("hideName", None)
        if hide_name is not None and self.show_hide_group is not None:
            hide = GroupManager.getObject(self.show_hide_group, hide_name)

        fade = None
        fade_name = fade_data.get("fade_movie", None)
        if fade_name is not None and self.fade_group is not None:
            fade = GroupManager.getObject(self.fade_group, fade_name)

        window = None
        window_name = fade_data.get("window_movie", None)
        if window_name is not None and self.window_group is not None:
            window = GroupManager.getObject(self.window_group, window_name)

        window_text = fade_data.get("window_text", None)

        skip = None
        if self.skip_button_name is not None and self.skip_group is not None:
            skip = GroupManager.getObject(self.skip_group, self.skip_button_name)

        return show, hide, fade, window, window_text, skip

    def __cbTutorialFadeShow(self, fade_id):
        """
        Show tutorial fade with attached 'components' (fade, window, skip) by custom fade id
        """

        SystemTutorialFade.setEnabled(True)
        SystemTutorialFade.setWorking(True)
        self.fade_id = fade_id
        self.cleanUp()

        if fade_id not in self.fades:
            return False

        self.current_scene = SceneManager.getCurrentSceneName()

        # Create local variables by custom fade_id
        self.movie_show, _, fade, window, window_text, skip = self.getFadeObjects(fade_id)

        if TaskManager.existTaskChain("TutorialFadeShow"):
            TaskManager.cancelTaskChain("TutorialFadeShow")

        with TaskManager.createTaskChain(Name="TutorialFadeShow", GroupName=self.show_hide_group) as tc:
            with GuardBlockInput(tc) as guard_source:
                guard_source.addEnable(self.movie_show)

                guard_source.addFunction(self.objAttach, self.movie_show, fade, self.fade_slot)
                guard_source.addFunction(self.setTextAlias, self.window_alias, window_text)
                guard_source.addFunction(self.objAttach, self.movie_show, window, self.window_slot)
                guard_source.addFunction(self.objAttach, self.movie_show, skip, self.skip_slot)

                guard_source.addTask("TaskMoviePlay", Movie=self.movie_show)

                guard_source.addNotify(Notificator.onTutorialFadeShowEnd, fade_id)

        return False

    def __cbTutorialFadeHide(self, fade_id=None):
        """
        Hide tutorial fade with attached 'components' (fade, window, skip) by custom fade id
        """

        SystemTutorialFade.setEnabled(False)
        SystemTutorialFade.setWorking(False)
        self.current_scene = None

        if self.fade_id is None:
            return False

        # Create local variables by custom fade_id
        show, self.movie_hide, fade, window, window_text, skip = self.getFadeObjects(self.fade_id)

        if TaskManager.existTaskChain("TutorialFadeHide"):
            TaskManager.cancelTaskChain("TutorialFadeHide")

        with TaskManager.createTaskChain(Name="TutorialFadeHide", GroupName=self.show_hide_group) as tc:
            with GuardBlockInput(tc) as guard_source_Hide:
                guard_source_Hide.addDisable(show)
                guard_source_Hide.addEnable(self.movie_hide)

                guard_source_Hide.addFunction(self.objAttach, self.movie_hide, fade, self.fade_slot)
                guard_source_Hide.addFunction(self.setTextAlias, self.window_alias, window_text)
                guard_source_Hide.addFunction(self.objAttach, self.movie_hide, window, self.window_slot)
                guard_source_Hide.addFunction(self.objAttach, self.movie_hide, skip, self.skip_slot)

                guard_source_Hide.addTask("TaskMoviePlay", Movie=self.movie_hide)
                guard_source_Hide.addDisable(self.movie_hide)

                guard_source_Hide.addFunction(self.objDetach, skip)
                guard_source_Hide.addFunction(self.removeTextAlias, self.window_alias)
                guard_source_Hide.addFunction(self.objDetach, window)
                guard_source_Hide.addFunction(self.objDetach, fade)

                guard_source_Hide.addNotify(Notificator.onTutorialFadeHideEnd, fade_id)

        self.fade_id = None

        return False

    def setTextAlias(self, alias, text_id):
        """
        Set text to alias
        Check if text is None, if True then set 'ID_EMPTY'
        """

        if alias is None:
            return

        if text_id is None:
            Mengine.setTextAlias("", alias, "ID_EMPTY")
        else:
            Mengine.setTextAlias("", alias, text_id)

    def removeTextAlias(self, alias):
        """
        Simple remove alias arguments
        """

        if alias is None:
            return

        Mengine.removeTextAliasArguments("", alias)

    def objAttach(self, movie, obj, slot_name):
        """
        Attach object to movie on slot_name and enable
        Check all arguments if any argument is None
        """

        args = [
            movie,
            obj,
            slot_name
        ]

        for arg in args:
            if arg is None:
                return

        if movie.hasSlot(slot_name) is False:
            return

        obj.setEnable(True)
        obj.returnToParent()

        node = obj.getEntityNode()

        slot = movie.getMovieSlot(slot_name)
        slot.addChild(node)

    def objDetach(self, obj):
        """
        Detach object from parent and disable
        Check if object is None
        """

        if obj is None:
            return

        obj.setEnable(False)
        obj.returnToParent()

    def notifySpicke(self, name, enabler):
        if name is None:
            return False

        obj = GroupManager.getObject(self.fade_group, name)

        if obj is None:
            return False

        if enabler == "Enable":
            obj.setEnable(True)

        elif enabler == "Disable":
            obj.setEnable(False)

        return False

    def _onStop(self):
        tcs = [
            "TutorialFadeShow",
            "TutorialFadeHide"
        ]

        for tc in tcs:
            if TaskManager.existTaskChain(tc):
                TaskManager.cancelTaskChain(tc)

    def _onSave(self):
        data_save = (self.fade_id, self.is_skipped, self.is_working, self.current_scene)
        return data_save

    def _onLoad(self, data_save):
        self.fade_id, self.is_skipped, self.is_working, self.current_scene = data_save

    @staticmethod
    def setWorking(state):
        SystemTutorialFade.is_working = bool(state)

    @staticmethod
    def setEnabled(state):
        SystemTutorialFade.is_enabled = bool(state)
