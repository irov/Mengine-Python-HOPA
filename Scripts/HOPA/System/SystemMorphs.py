from Event import Event
from Foundation.DefaultManager import DefaultManager
from Foundation.GroupManager import GroupManager
from Foundation.SceneManager import SceneManager
from Foundation.System import System
from Foundation.SystemManager import SystemManager
from Foundation.Utils import isCollectorEdition
from HOPA.MorphManager import MorphManager
from Notification import Notification


# Confluence doc: https://wonderland-games.atlassian.net/wiki/spaces/HOG/pages/1858666545/Morphs


class SystemMorphs(System):
    s_dev_to_debug = False

    # list of morph ids:
    s_scene_morphs = []
    s_picked_morphs = []
    s_active_morphs = []

    def __init__(self):
        super(SystemMorphs, self).__init__()
        self.morphs = {}  # { morphId: SystemMorphs.Morph, ... }
        self.scene_morphs = []  # [ Morph, ... ]

    def _onRun(self):
        SystemMorphs.s_scene_morphs = []
        SystemMorphs.s_picked_morphs = []
        SystemMorphs.s_active_morphs = []

        if self.isMorphsEnabled() is True:
            self.__addDevToDebug()
            self._addObservers()
            self.__activateKeyCheats()
        else:
            self.disableMorphs()

        return True

    def _onStop(self):
        for morph in self.morphs.values():
            morph.cleanUp()
        self.morphs = {}

        if self.existTaskChain("SystemMorphsAction") is True:
            self.removeTaskChain("SystemMorphsAction")

        if self.existTaskChain("SystemMorphs_DevToDebug") is True:
            self.removeTaskChain("SystemMorphs_DevToDebug")

        if self.existTaskChain("SystemMorphsCheats") is True:
            self.removeTaskChain("SystemMorphsCheats")

    # ---

    @staticmethod
    def isMorphsEnabled():
        is_enabled = DefaultManager.getDefaultBool("EnableMorphs", False) is True

        if DefaultManager.getDefaultBool("MorphsOnlyForCE", True) is True:
            collector_edition = isCollectorEdition()
            return all([is_enabled, collector_edition])

        return is_enabled

    @staticmethod
    def disableMorphs():
        for params in MorphManager.getAllMorphs():
            group = GroupManager.getGroup(params.group_name)

            for state, movie_name in params.state_movies.items():
                movie = group.getObject(movie_name)
                movie.setEnable(False)

    def initMorphs(self):
        for params in MorphManager.getAllMorphs():
            morph = Morph(params)

            group = GroupManager.getGroup(params.group_name)
            for state, movie_name in params.state_movies.items():
                movie = group.getObject(movie_name)
                morph.addState(state, movie)

            self.morphs[morph.id] = morph

            if morph.id not in SystemMorphs.s_picked_morphs:
                if morph.id in SystemMorphs.s_active_morphs:
                    continue
                SystemMorphs.s_active_morphs.append(morph.id)

        if self.isMorphsEnabled() is True:
            self.reportMorphStatus()

    def reportMorphStatus(self, scene_morphs=False, show_ids=False):
        if _DEVELOPMENT is False:
            return

        Trace.msg(" MORPHS STATUS ".center(50, "-"))

        Trace.msg("inited Morphs:  ".rjust(25) + str(len(self.morphs)))
        Trace.msg("active:  ".rjust(25) + str(len(SystemMorphs.s_active_morphs)))
        if show_ids is True:
            Trace.msg(str(SystemMorphs.s_active_morphs))
        Trace.msg("picked:  ".rjust(25) + str(len(SystemMorphs.s_picked_morphs)))
        if show_ids is True:
            Trace.msg(str(SystemMorphs.s_picked_morphs))
        if scene_morphs is True:
            Trace.msg("current:  ".rjust(25) + str(len(self.scene_morphs)))
            if show_ids is True:
                Trace.msg(str(SystemMorphs.s_scene_morphs))

        Trace.msg("-" * 50)

    def start(self):
        if len(self.scene_morphs) == 0:
            return

        if self.existTaskChain("SystemMorphsAction") is True:
            # Trace.msg_err("SystemMorph has already activate morphs")
            return

        def _cb(isSkip):
            cur_scene = SceneManager.getCurrentSceneName()
            # todo: may be do last check is scene has not morphs
            Notification.notify(Notificator.onMorphsSceneComplete, cur_scene)
            self.checkPickedMorphs()

        with self.createTaskChain("SystemMorphsAction", Cb=_cb) as tc:
            for morph, parallel in tc.addParallelTaskList(self.scene_morphs):
                with parallel.addRepeatTask() as (repeat, until):
                    repeat.addScope(morph.scopeMorphing)
                    until.addScope(morph.scopeClick)
                parallel.addScope(morph.scopePick)  # next behavior view in observer-method _onMorphPick

    def checkPickedMorphs(self):
        if len(self.morphs) == len(SystemMorphs.s_picked_morphs):
            Notification.notify(Notificator.onAllMorphsPicked)

    def _addSceneMorph(self, morph):
        if morph in self.scene_morphs:
            return False

        self.scene_morphs.append(morph)
        SystemMorphs.s_scene_morphs.append(morph.id)
        return True

    def _removeSceneMorph(self, morph_or_id):
        """ JUST REMOVE Morph BY ITS id FROM *self.scene_morphs* AND THAT'S ALL

            :returns: True if morph removed from scene_morphs or False if no """

        if isinstance(morph_or_id, Morph):
            morph = morph_or_id
            if morph in self.scene_morphs:
                self.scene_morphs.remove(morph)
                SystemMorphs.s_scene_morphs.remove(morph.id)
                return True
        else:
            morph_id = morph_or_id
            for morph in self.scene_morphs:
                if morph.id != morph_id:
                    continue

                self.scene_morphs.remove(morph)
                SystemMorphs.s_scene_morphs.remove(morph_id)
                return True

        return False

    # --- Cheats

    def cheatSceneMorphReset(self):
        def _report():
            Trace.msg(" CHEAT SCENE RESTART ".center(50, "-"))
            Trace.msg("  active:", SystemMorphs.s_active_morphs)
            Trace.msg("  picked:", SystemMorphs.s_picked_morphs)
            Trace.msg("   scene:", self.scene_morphs)
            Trace.msg("-" * 50)

        cur_scene = SceneManager.getCurrentSceneName()
        scene_groups = SceneManager.getSceneGroups(cur_scene)

        _report()

        for morph_id in SystemMorphs.s_picked_morphs:
            morph = self.morphs[morph_id]
            if morph.params.group_name not in scene_groups:
                continue

            SystemMorphs.s_active_morphs.append(morph_id)
            SystemMorphs.s_picked_morphs.remove(morph_id)
            self._addSceneMorph(morph)

        for morph in self.scene_morphs:
            morph.disableMovies()

        _report()

        if self.existTaskChain("SystemMorphsAction") is True:
            self.removeTaskChain("SystemMorphsAction")
        self.start()

    def __activateKeyCheats(self):
        if _DEVELOPMENT is False:
            return
        if Mengine.hasOption("cheats") is False:
            return

        def checkEditBox():
            if SystemManager.hasSystem("SystemEditBox"):
                system_edit_box = SystemManager.getSystem("SystemEditBox")
                if system_edit_box.hasActiveEditbox():
                    return False
            return True

        with self.createTaskChain("SystemMorphsCheats", Repeat=True) as tc:
            with tc.addRaceTask(2) as (tc_0, tc_1):
                tc_0.addTask('TaskKeyPress', Keys=[DefaultManager.getDefaultKey("DevCheatMorphSceneReset", "VK_2")])
                with tc_0.addIfTask(checkEditBox) as (tc_true, _):
                    tc_true.addNotify(Notificator.onMorphsCheatSceneReset)

                tc_1.addTask('TaskKeyPress', Keys=[DefaultManager.getDefaultKey("DevCheatMorphsReport", "VK_3")])
                with tc_0.addIfTask(lambda: checkEditBox()) as (tc_true, _):
                    tc_true.addFunction(self.reportMorphStatus, True, True)

    def __addDevToDebug(self):
        if Mengine.isAvailablePlugin("DevToDebug") is False:
            return
        if SystemMorphs.s_dev_to_debug is True:
            return
        SystemMorphs.s_dev_to_debug = True

        tab = Mengine.getDevToDebugTab("Cheats") or Mengine.addDevToDebugTab("Cheats")

        w_title = Mengine.createDevToDebugWidgetText("morphs_title")
        w_title.setText("Morphs:")
        tab.addWidget(w_title)

        w_restart = Mengine.createDevToDebugWidgetButton("morphs_scene_restart")
        w_restart.setTitle("Restore scene morphs")
        w_restart.setClickEvent(Notification.notify, Notificator.onMorphsCheatSceneReset)
        tab.addWidget(w_restart)

        w_report = Mengine.createDevToDebugWidgetButton("morphs_report")
        w_report.setTitle("Report morphs status")
        w_report.setClickEvent(self.reportMorphStatus, True, True)
        tab.addWidget(w_report)

        w_separator = Mengine.createDevToDebugWidgetText("morphs_separator_text")
        w_separator.setText("---")
        tab.addWidget(w_separator)

        def _onSceneActivate(scene_name):
            if len(self.scene_morphs) == 0:
                w_restart.setHide(True)
            else:
                w_restart.setHide(False)
            return False

        with self.createTaskChain("SystemMorphs_DevToDebug", Repeat=True) as tc:
            tc.addListener(Notificator.onSceneActivate, Filter=_onSceneActivate)

    # ---

    def _addObservers(self):
        self.addObserver(Notificator.onSceneActivate, self._onSceneActivate)
        self.addObserver(Notificator.onSceneDeactivate, self._onSceneDeactivate)
        self.addObserver(Notificator.onMorphsCheatSceneReset, self._onMorphsCheatSceneReset)
        self.addObserver(Notificator.onMorphPicked, self._onMorphPicked)

    def _onSceneActivate(self, scene_name):
        scene_groups = SceneManager.getSceneGroups(scene_name)

        for morph in self.morphs.values():
            if morph.id in SystemMorphs.s_picked_morphs:
                continue
            if morph.params.group_name not in scene_groups:
                continue

            parent_movie = GroupManager.getObject(morph.params.group_name, morph.params.parent_movie_name)
            if parent_movie.hasSlot(morph.params.slot_name) is False:
                Trace.log("System", 0, "SystemMorph find error for morph [{}]: movie {!r} [{}] not found slot {!r}".format(
                    morph.id, morph.params.parent_movie_name, morph.params.group_name, morph.params.slot_name))
                self.morphs.pop(morph.id)
                morph.disableMovies()
                morph.cleanUp()
                continue

            slot = parent_movie.getMovieSlot(morph.params.slot_name)
            morph.setSlot(slot)

            self._addSceneMorph(morph)

        self.start()
        return False

    def _onSceneDeactivate(self, scene_name):
        if self.existTaskChain("SystemMorphsAction") is True:
            self.removeTaskChain("SystemMorphsAction")

        for morph in self.scene_morphs:
            morph.removeSlot()
            self._removeSceneMorph(morph)
        self.scene_morphs = []

        return False

    def _onMorphsCheatSceneReset(self):
        self.cheatSceneMorphReset()
        return False

    def _onMorphPicked(self, morph_id):
        SystemMorphs.s_picked_morphs.append(morph_id)
        SystemMorphs.s_active_morphs.remove(morph_id)

        if self._removeSceneMorph(morph_id) is False:
            if _DEVELOPMENT is True:
                Trace.msg_err("Morph {!r} not found in self.scene_morphs, so self._removeSceneMorph returns False!".format(morph_id))

        Notification.notify(Notificator.onAddAchievementPlateToQueue, 'Morphs', morph_id)

        return False

    # ---

    @staticmethod
    def getActiveMorphIDs():
        return SystemMorphs.s_active_morphs

    @staticmethod
    def getPickedMorphIDs():
        return SystemMorphs.s_picked_morphs

    @staticmethod
    def getAllMorphIDs():
        return SystemMorphs.s_active_morphs + SystemMorphs.s_picked_morphs

    @staticmethod
    def getSceneMorphIDs():
        return SystemMorphs.s_scene_morphs

    # ---

    def _onSave(self):
        self.initMorphs()

        dict_save = {"active_morphs": SystemMorphs.s_active_morphs, "picked_morphs": SystemMorphs.s_picked_morphs}

        return dict_save

    def _onLoad(self, dict_save):
        SystemMorphs.s_active_morphs = dict_save.get("active_morphs", [])
        SystemMorphs.s_picked_morphs = dict_save.get("picked_morphs", [])

        self.initMorphs()

        return


class Morph(object):
    EVENT_STATE_CHANGE = Event("MorphStateChange")

    def __init__(self, params):
        self.params = params  # MorphManager.MorphParams
        self.id = params.id
        self.movies = {}  # {state: movie2}
        self.slot = None  # slot
        self.state = None

    def __repr__(self):
        return "<Morph [{}] in state {}>".format(self.id, self.state)

    def scopeMorphing(self, source):
        # print "morphing...", self.id, self.getCurrentState()
        settings = self.params.settings
        idle_movie = self.getMovieState("Idle")

        source.addDelay(settings.anim_delay)
        source.addFunction(self.setState, "Idle")
        source.addPlay(idle_movie, Wait=True, Loop=False)

    def scopeClick(self, source):
        idle_movie = self.getMovieState("Idle")

        with source.addIfTask(lambda: self.getCurrentState() != "Idle") as (wait, _):
            wait.addEvent(Morph.EVENT_STATE_CHANGE,
                          Filter=lambda morph, state: all([morph.id == self.id, state == "Idle"]))
        source.addTask("TaskMovie2SocketClick", Movie2=idle_movie, SocketName="socket")

    def scopePick(self, source):
        pick_movie = self.getMovieState("Pick")
        idle_movie = self.getMovieState("Idle")

        source.addNotify(Notificator.onMorphPicked, self.id)
        source.addTask("TaskMovie2Stop", Movie2=idle_movie)
        source.addFunction(self.setState, "Pick")
        source.addPlay(pick_movie, Loop=False, Wait=True)
        source.addFunction(pick_movie.setLastFrame, True)
        source.addFunction(self.setState, None)

    def setSlot(self, slot):
        if self.slot is not None:
            Trace.log("Entity", 0, "Morph {!r} has already slot".format(self.id))
            return

        for movie in self.movies.values():
            node = movie.getEntityNode()
            slot.addChild(node)
        self.slot = slot

    def addState(self, state, movie):
        if self.slot is not None:
            Trace.log("Entity", 0, "Can't add state {!r} to morph [{}]: configure slot".format(state, self.id))
            return

        movie.setEnable(False)
        if self.slot:
            self.slot.addChild(movie)
        self.movies[state] = movie

    def getCurrentState(self):
        return self.state

    def getMovieState(self, state):
        return self.movies.get(state)

    def getCurrentMovie(self):
        cur_state = self.getCurrentState()
        cur_movie = self.movies[cur_state]
        return cur_movie

    def setState(self, state):
        if state is None:
            self.setNone()
            return
        if state not in self.movies:
            Trace.log("Entity", 0, "SystemMorph can't set state {!r} to morph [{}]: not found".format(state, self.id))
            return

        cur_state = self.getCurrentState()
        if cur_state is not None and state != cur_state:
            cur_movie = self.movies[cur_state]
            cur_movie.setEnable(False)

        movie = self.movies[state]
        movie.setEnable(True)

        self.state = state
        Morph.EVENT_STATE_CHANGE(self, state)

        return movie

    def setNone(self):
        cur_state = self.getCurrentState()
        if cur_state is not None:
            cur_state_movie = self.getCurrentMovie()
            cur_state_movie.setEnable(False)
            cur_state_movie.setPlay(False)
        self.state = None

    def removeSlot(self):
        for movie in self.movies.values():
            movie.returnToParent()
        self.slot = None

    def cleanUp(self):
        self.removeSlot()
        self.movies = None
        self.params = None

    def disableMovies(self):
        for movie in self.movies.values():
            movie.setPlay(False)
            movie.setLastFrame(False)
            movie.setEnable(False)
        self.state = None
