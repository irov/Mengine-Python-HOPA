from Foundation.DefaultManager import DefaultManager
from Foundation.DemonManager import DemonManager
from Foundation.GroupManager import GroupManager
from Foundation.GuardBlockInput import GuardBlockInput
from Foundation.SceneManager import SceneManager
from Foundation.System import System
from Foundation.SystemManager import SystemManager
from HOPA.JournalManager import JournalManager
from Notification import Notification


SCENE_EFFECT_MOVIE_OPEN = "Movie2_Open"
SCENE_EFFECT_MOVIE_CLOSE = "Movie2_Close"


class SystemJournal(System):
    s_dev_to_debug = False

    def __init__(self):
        super(SystemJournal, self).__init__()
        self.demon_journal = DemonManager.getDemon("Journal")
        self.current_scene = None
        self.current_page = None

    def _onRun(self):
        self.addObserver(Notificator.onJournalAddPage, self.__onJournalAdd)
        self.addObserver(Notificator.onJournalSetPage, self.__onJournalSet)

        self.__runTaskChains()
        self.__cheatAddAllPages()

        return True

    def _onStop(self):
        if self.existTaskChain("SystemJournalCheat"):
            self.removeTaskChain("SystemJournalCheat")

    def __scopeOpen(self, source, group_name):
        source.addScope(self.__scopeSceneEffect, group_name, SCENE_EFFECT_MOVIE_OPEN)

    def __scopeClose(self, source, group_name):
        source.addScope(self.__scopeSceneEffect, group_name, SCENE_EFFECT_MOVIE_CLOSE)

    def __scopeSceneEffect(self, source, group_name, movie_name):
        if not GroupManager.hasObject(group_name, movie_name):
            return
        scene_effect_movie = GroupManager.getObject(group_name, movie_name)
        with GuardBlockInput(source) as guard_source:
            with guard_source.addParallelTask(2) as (guard_source_movie, guard_source_fade):
                guard_source_movie.addTask("TaskMovie2Play", Movie2=scene_effect_movie, Wait=True, AutoEnable=True)

    def __checkIsAllJournalUnlocked(self):
        unlocked_pages = self.demon_journal.getParam("Pages")
        unlocked_pages_count = len(unlocked_pages)
        all_pages_count = len(JournalManager.getAllPages())

        if unlocked_pages_count == all_pages_count:
            Notification.notify(Notificator.onJournalAllPagesFound)

    def __onJournalAdd(self, journal_id):
        self.demon_journal = DemonManager.getDemon("Journal")

        if not self.demon_journal.hasPage(journal_id):
            self.demon_journal.appendParam("Pages", journal_id)
            self.__checkIsAllJournalUnlocked()  # for achievement

        self.demon_journal.setParam("CurrentPage", journal_id)
        self.current_page = journal_id

        return False

    def __onJournalSet(self, journal_id):
        self.demon_journal = DemonManager.getDemon("Journal")
        self.demon_journal.setCurrentPage(journal_id)
        self.current_page = journal_id
        return False

    def __onJournalClose(self, journal_id=None):
        self.demon_journal = DemonManager.getDemon("Journal")
        entity = self.demon_journal.getEntity()
        entity.onCloseJournal()

        return False

    def __runTaskChains(self):
        time_out_from = 0.75
        time_out_time = 0.5 * 2000  # speed fix
        time_in_to = 0.75
        time_in_time = 0.25 * 4000
        fade_group = "FadeJournal"

        if GroupManager.hasGroup("Journal") is False:
            return

        self.demon_journal = DemonManager.getDemon("Journal")
        if self.demon_journal.hasObject("Movie2Button_Play") is True:
            self.__cutScenePlay()

        with self.createTaskChain(Name="JournalClose_But", Repeat=True) as tc_close:
            tc_close.addTask("TaskMovie2ButtonClick", GroupName="Journal", Movie2ButtonName="Movie2Button_Close")
            tc_close.addNotify(Notificator.onJournalClose)

        with self.createTaskChain(Name="JournalOpen", Global=True, Repeat=True) as tc_open:
            tc_open.addTask("TaskMovie2ButtonClick", GroupName="Open_Journal", Movie2ButtonName="Movie2Button_Journal")
            if GroupManager.hasGroup(fade_group):
                with GuardBlockInput(tc_open) as guard_journal:
                    with guard_journal.addParallelTask(2) as (tc_fade, tc_open_journal):
                        tc_fade.addTask("AliasFadeIn", FadeGroupName=fade_group, To=time_in_to, Time=time_in_time)

                        tc_open_journal.addNotify(Notificator.onJournalOpen)
                        tc_open_journal.addTask("TaskSceneLayerGroupEnable", LayerName="Journal", Value=True)
                        tc_open_journal.addScope(self.__scopeOpen, "Journal")
            else:
                tc_open.addNotify(Notificator.onJournalOpen)
                tc_open.addTask("TaskSceneLayerGroupEnable", LayerName="Journal", Value=True)

        with self.createTaskChain(Name="JournalClose", Repeat=True) as tc_close:
            tc_close.addListener(Notificator.onJournalClose)

            if GroupManager.hasGroup(fade_group):
                with GuardBlockInput(tc_close) as guard_journal:
                    with guard_journal.addParallelTask(2) as (tc_fade_out, tc_close_journal):
                        tc_fade_out.addTask("AliasFadeOut", FadeGroupName=fade_group, From=time_out_from, Time=time_out_time)

                        tc_close_journal.addScope(self.__scopeClose, "Journal")

            tc_close.addFunction(self.__onJournalClose)

            tc_close.addTask("TaskSceneLayerGroupEnable", LayerName="Journal", Value=False)

        with self.createTaskChain(Name="JournalAppend", Global=True, Repeat=True, GroupName="Open_Journal") as tc:
            tc.addListener(Notificator.onJournalAddPage)
            tc.addScope(self._scopeJournalAppend)

            with tc.addRepeatTask() as (tc_new, tc_open):
                tc_new.addListener(Notificator.onJournalAddPage)
                tc_new.addScope(self._scopeJournalAppend)

                tc_open.addListener(Notificator.onJournalOpen)
                tc_open.addTask("TaskSetParam", ObjectName="Movie2_Env_Llight_loop", Param="Loop", Value=False)
                tc_open.addTask("TaskMovie2Stop", Movie2Name="Movie2_Env_Llight_loop")

    def _scopeJournalAppend(self, source):
        group = GroupManager.getGroup("Open_Journal")
        if group.isActive() is False:
            source.addListener(Notificator.onLayerGroupEnable, Filter=lambda name: name == "Open_Journal")

        source.addTask("TaskEnable", ObjectName="Movie2_Env_Llight_loop", Value=False)
        source.addTask("TaskEnable", ObjectName="Movie2Button_Journal", Value=False)

        source.addTask("TaskMovie2Play", Movie2Name="Movie2_Env_Activate", Wait=True, AutoEnable=True)

        source.addTask("TaskEnable", ObjectName="Movie2_Env_Llight_loop", Value=True)
        source.addTask("TaskMovie2Play", Movie2Name="Movie2_Env_Llight_loop", Wait=False, Loop=True)

        source.addTask("TaskEnable", ObjectName="Movie2Button_Journal", Value=True)

    def __cutScenePlay(self):
        self.movie2button_play = self.demon_journal.getObject("Movie2Button_Play")

        if self.existTaskChain('Journal_CutScene'):
            self.removeTaskChain('Journal_CutScene')

        with self.createTaskChain(Name="Journal_CutScene", Repeat=True) as tc:
            tc.addTask("TaskMovie2ButtonClick", Movie2Button=self.movie2button_play)
            tc.addFunction(self.__curentSceneSave)
            tc.addScope(self.__scopePlay)

    def __scopePlay(self, source):
        page = JournalManager.getJournalPage(self.current_page)
        source.addTask("TaskCutScenePlay", CutSceneName=page.cutScene, Transition=True)
        source.addTask("AliasTransition", SceneName=self.current_scene)
        source.addFunction(self.__currentSceneDone)

    def __curentSceneSave(self):
        self.current_scene = SceneManager.getCurrentSceneName()

    def __currentSceneDone(self):
        self.current_scene = None

    def __cutSceneReplay(self):
        if self.existTaskChain('Journal_CutScene_replay'):
            self.removeTaskChain('Journal_CutScene_replay')

        with self.createTaskChain(Name="Journal_CutScene_replay", Repeat=False) as tc:
            tc.addScope(self.__scopePlay)

    def _onSave(self):
        return self.current_scene, self.current_page

    def _onLoad(self, data_save):
        if data_save is None:
            return

        self.current_scene, self.current_page = data_save
        if self.current_scene is not None:
            self.__cutSceneReplay()

    def __cheatAddAllPages(self):
        if Mengine.hasOption('cheats') is False:
            return

        def __addAllPages(widget=None):
            pages = JournalManager.getOrderedAllJournalIDs()
            for pageID in pages:
                Notification.notify(Notificator.onJournalAddPage, pageID)
            if widget is not None:
                widget.setHide(True)

            Trace.msg("<Cheats> All journal pages unlocked by cheats")

        def checkEditBox():
            if SystemManager.hasSystem("SystemEditBox"):
                system_edit_box = SystemManager.getSystem("SystemEditBox")
                if system_edit_box.hasActiveEditbox():
                    return False
            return True

        with self.createTaskChain("SystemJournalCheat") as tc:
            tc.addTask("TaskKeyPress", Keys=[DefaultManager.getDefaultKey("CheatsJournalAddAllPages", 'VK_M')])
            with tc.addIfTask(checkEditBox) as (tc_true, _):
                tc_true.addFunction(__addAllPages)

        if Mengine.isAvailablePlugin("DevToDebug") is False:
            return
        if SystemJournal.s_dev_to_debug is True:
            return
        SystemJournal.s_dev_to_debug = True

        tab = Mengine.getDevToDebugTab("Cheats") or Mengine.addDevToDebugTab("Cheats")
        widget = Mengine.createDevToDebugWidgetButton("journal_all_pages")
        widget.setTitle("Get all Journal pages")
        widget.setClickEvent(__addAllPages, widget)
        tab.addWidget(widget)
