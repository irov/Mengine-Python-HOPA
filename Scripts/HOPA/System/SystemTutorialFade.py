from Foundation.GroupManager import GroupManager
from Foundation.GuardBlockInput import GuardBlockInput
from Foundation.SceneManager import SceneManager
from Foundation.System import System
from Foundation.TaskManager import TaskManager
from HOPA.TutorialFadesManager import TutorialFadesManager


_debug = False


class SystemTutorialFade(System):
    is_working = False
    is_enabled = False

    def __init__(self):
        super(SystemTutorialFade, self).__init__()
        self.param = None
        self.tc = None
        self.movie_show = None
        self.movie_fade = None
        self.fade_id = None
        self.is_skipped = False
        self.current_scene = None

    def _onRun(self):
        self.param = TutorialFadesManager.getParam()
        self.button = GroupManager.getObject("SkipTutorial", "Movie2Button_Skip")

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
        self.addObserver(Notificator.onSceneDeactivate, self.starterClinner)
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
        self.starterClinner()
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
                    if slot.hasSlotsGroup("FadeTutorial"):
                        self.__cbTutorialFadeShow(self.fade_id)
                else:
                    self.starterClinner()
        else:
            self.starterClinner()

        return False

    def starterClinner(self, some_args=None, some_other_args=None):
        if self.is_skipped:
            return False

        for key in self.param:
            fade_data = self.param[key]
            show_name = fade_data.showName
            hide_name = fade_data.hideName
            movie_group_name = fade_data.groupName

            self.movie_show = GroupManager.getObject(movie_group_name, show_name)
            if self.movie_show is not None:
                self.movie_show.setEnable(False)

            self.movie_fade = GroupManager.getObject(movie_group_name, hide_name)
            if self.movie_fade is not None:
                self.movie_fade.setEnable(False)

        self.button.returnToParent()

        return False

    def __cbTutorialFadeShow(self, fade_id):
        SystemTutorialFade.setEnabled(True)
        SystemTutorialFade.setWorking(True)
        self.fade_id = fade_id
        self.starterClinner()

        if _debug:
            print("__cbTutorialFadeShow | self.fade_id={!r}".format(self.fade_id))

        if fade_id not in self.param:
            return False

        self.current_scene = SceneManager.getCurrentSceneName()
        fade_data = self.param[fade_id]
        show_name = fade_data.showName

        movie_group_name = fade_data.groupName
        movie_group = GroupManager.getGroup(movie_group_name)
        self.movie_show = GroupManager.getObject(movie_group_name, show_name)

        with TaskManager.createTaskChain(Name="TutorialFade", Group=movie_group) as tc:
            with GuardBlockInput(tc) as guard_source:
                if _debug:
                    guard_source.addPrint("      show: ...fade start show | fade_id={!r}, self={!r}".format(fade_id, self.fade_id))
                guard_source.addTask("TaskEnable", ObjectName=show_name, Value=True)
                guard_source.addFunction(self.buttonAttach, self.movie_show)
                guard_source.addTask("TaskMoviePlay", MovieName=show_name)
                if _debug:
                    guard_source.addPrint("      show: fade start end... | fade_id={!r}, self={!r}".format(fade_id, self.fade_id))

        return False

    def __cbTutorialFadeHide(self, fade_id=None):
        SystemTutorialFade.setEnabled(False)
        SystemTutorialFade.setWorking(False)
        self.current_scene = None

        if _debug:
            print("__cbTutorialFadeHide | self.fade_id={!r}".format(self.fade_id))

        if self.fade_id is None:
            return False

        fade_data = self.param[self.fade_id]
        show_name = fade_data.showName
        hide_name = fade_data.hideName
        movie_group_name = fade_data.groupName
        movie_group = GroupManager.getGroup(movie_group_name)

        self.movie_fade = GroupManager.getObject(movie_group_name, hide_name)

        with TaskManager.createTaskChain(Name="TutorialFadeHide", Group=movie_group) as tc:
            with GuardBlockInput(tc) as guard_source_Hide:
                if _debug:
                    guard_source_Hide.addPrint("      hide: ...fade start hide | self fade_id={!r}".format(self.fade_id))
                guard_source_Hide.addTask("TaskEnable", ObjectName=show_name, Value=False)
                guard_source_Hide.addFunction(self.buttonAttach, self.movie_fade)
                guard_source_Hide.addTask("TaskEnable", ObjectName=hide_name, Value=True)

                guard_source_Hide.addTask("TaskMoviePlay", MovieName=hide_name)
                guard_source_Hide.addTask("TaskEnable", ObjectName=hide_name, Value=False)
                guard_source_Hide.addFunction(self.buttonDeAttach)
                if _debug:
                    guard_source_Hide.addPrint("      hide: fade end hide... |  self fade_id={!r}".format(self.fade_id))

        self.fade_id = None

        return False

    def buttonAttach(self, movie):
        self.button.setEnable(True)
        self.button.returnToParent()

        node = self.button.getEntityNode()

        slot = movie.getMovieSlot("slot")
        slot.addChild(node)

    def buttonDeAttach(self):
        self.button.returnToParent()

    def notifySpicke(self, name, enabler):
        if name is None:
            return False

        obj = GroupManager.getObject("FadeTutorial", name)

        if enabler == "Enable":
            obj.setEnable(True)

        elif enabler == "Disable":
            obj.setEnable(False)

        return False

    def tcEnd(self, arg=None):
        if TaskManager.existTaskChain("TutorialFadeHide"):
            TaskManager.cancelTaskChain("TutorialFadeHide")

        if TaskManager.existTaskChain("TutorialFade"):
            TaskManager.cancelTaskChain("TutorialFade")

    def _onStop(self):
        self.tcEnd()

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
