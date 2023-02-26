from Foundation.GroupManager import GroupManager
from Foundation.Notificator import Notificator
from Foundation.SceneManager import SceneManager
from Foundation.System import System
from Foundation.SystemManager import SystemManager
from HOPA.ChapterSelectionManager import ChapterSelectionManager
from HOPA.Entities.Map2.Map2Manager import Map2Manager
from HOPA.SemaphoreManager import SemaphoreManager
from HOPA.StageManager import StageManager
from Notification import Notification

class Chapter(object):
    def __init__(self, param):
        self.chapter_name = param.chapter_name
        self.param = param
        self.is_blocked = False  # don't play open anim even is_open is True
        self.is_open = param.is_open if param.is_main_chapter is False else True
        # self.is_open = True  # debug
        self.is_play_open_animation = False
        self.is_played = False  # if chapter was picked/played already  # self.is_played = True  # debug

    def isOpen(self):
        return self.is_open

    def isBlocked(self):
        return self.is_blocked

    def setBlocked(self, value):
        self.is_blocked = bool(value)

    def setOpen(self, value):
        self.is_open = bool(value)

    def setOpenAnimationPlayed(self, value):
        self.is_play_open_animation = value

    def setPlayed(self, value):
        self.is_played = value

class SystemChapterSelection(System):
    s_dev_to_debug = False
    s_chapter_selections = {}

    # these methods would be called when player reset chapter (and create new account)
    staticmethod_onCreateNewAccount = []

    def __init__(self):
        super(SystemChapterSelection, self).__init__()

    def _onParams(self, params):
        pass

    def _onRun(self):
        chapter_selection_params = ChapterSelectionManager.getChapterSelectionParams()
        for chapter_selection_param in chapter_selection_params.values():
            chapter_selection = Chapter(chapter_selection_param)
            SystemChapterSelection.s_chapter_selections[chapter_selection_param.chapter_name] = chapter_selection

        ChapterSelectionManager.s_chapter_current = None

        self.__setObservers()

        self.__addDevToDebug()

        return True

    def __setObservers(self):
        self.addObserver(Notificator.onChapterSelectionChoseChapter, self.__cbChapterSelectionChoseChapter)
        self.addObserver(Notificator.onChapterSelectionBlock, self.__cbChapterBlock)
        self.addObserver(Notificator.onChapterOpen, self.__cbChapterOpen)
        self.addObserver(Notificator.onGameComplete, self.__cbGameComplete)
        self.addObserver(Notificator.onChapterSelectionResetProfile, self.__cbChapterSelectionResetProfile)

    def __cbChapterSelectionResetProfile(self, chapter_id):
        """
        Now no such thing as chapters. there are only main chapter and bonus chapter
        Only different is start_scene/start_cut_scene and map_group/map_demon for both

        So here we just reset account fully, but save some system params

        But actually somehow we can reset each scene_scenario_macro for scenes in main chapter or bonus chapter
        """
        cur_stage = StageManager.getCurrentStage()
        if cur_stage is None:
            return False

        chapter_param = ChapterSelectionManager.getChapterSelectionParam(chapter_id)

        old_params = {"Mute": Mengine.getCurrentAccountSetting("Mute"), "Fullscreen": Mengine.getCurrentAccountSettingBool("Fullscreen"), "Widescreen": Mengine.getCurrentAccountSetting("Widescreen"), "Cursor": Mengine.getCurrentAccountSetting("Cursor"), "CustomCursor": Mengine.getCurrentAccountSetting("CustomCursor"), "Name": Mengine.getCurrentAccountSetting("Name"), }
        slot_id = Mengine.getCurrentAccountSettingUInt("SlotID")
        slot_id_int = slot_id

        difficulty = {"Difficulty": Mengine.getCurrentAccountSetting("Difficulty"), "DifficultyCustomHintTime": Mengine.getCurrentAccountSetting("DifficultyCustomHintTime"), "DifficultyCustomSkipTime": Mengine.getCurrentAccountSetting("DifficultyCustomSkipTime"), "DifficultyCustomTutorial": Mengine.getCurrentAccountSetting("DifficultyCustomTutorial"), "DifficultyCustomSparklesOnActiveAreas": Mengine.getCurrentAccountSetting("DifficultyCustomSparklesOnActiveAreas"),
            "DifficultyCustomSparklesOnHOPuzzles": Mengine.getCurrentAccountSetting("DifficultyCustomSparklesOnHOPuzzles"), "DifficultyCustomPlusItemIndicated": Mengine.getCurrentAccountSetting("DifficultyCustomPlusItemIndicated"), "DifficultyCustomIndicatorsOnMap": Mengine.getCurrentAccountSetting("DifficultyCustomIndicatorsOnMap"), "DifficultyCustomChangeIconOnActiveAreas": Mengine.getCurrentAccountSetting("DifficultyCustomChangeIconOnActiveAreas"), }

        '''
        Restore saved systems
        '''
        systems_save = list()

        for system_name in chapter_param.on_chapter_reset_saved_systems:
            system = SystemManager.getSystem(system_name)
            save = system._onSave()
            # print '__cbChapterSelectionResetProfile save:', system_name, save
            systems_save.append((system, save))

        '''
        Complete saved paragraphs if those were completed before
        '''
        paragraphs_to_run = list()

        scenario_chapter = cur_stage.getScenarioChapter()

        for paragraph_name in chapter_param.on_chapter_reset_saved_paragraphs:
            paragraph_complete = scenario_chapter.isParagraphComplete(paragraph_name)
            if paragraph_complete:
                paragraphs_to_run.append(paragraph_name)  # print 'paragraph completed, added in list to complete in new account', paragraph_name

        account_id = Mengine.createAccount()

        def cbLoadSystems(account_id_):
            if account_id_ == account_id:
                for system_, save_ in systems_save:
                    system_._onLoad(save_)  # print '__cbChapterSelectionResetProfile load:', system_.__class__.__name__, save_

                return True

            return False

        def cbRunParagraphs(_stage_name):
            for _paragraph_name in paragraphs_to_run:
                Notification.notify(Notificator.onParagraphRun, _paragraph_name)  # print '__cbChapterSelectionResetProfile paragraph complete:', _paragraph_name

            return True

        self.addObserver(Notificator.onStageRun, cbRunParagraphs)
        self.addObserver(Notificator.onSessionNew, cbLoadSystems)

        '''
        Reset Chapter through creating new account
        '''

        Mengine.selectAccount(account_id)
        Mengine.changeCurrentAccountSetting("SlotID", unicode(slot_id))
        Mengine.changeCurrentAccountSetting("SessionSave", unicode(False))
        Mengine.changeCurrentAccountSettingBool("Default", False)
        for key, value in old_params.items():
            Mengine.changeCurrentAccountSetting(key, unicode(value))

        group_new_profile = GroupManager.getGroup("Profile_New")
        object_new_profile = group_new_profile.getObject("Demon_ProfileNew")
        object_new_profile.setAccountID(account_id)

        group_profile = GroupManager.getGroup("Profile")
        object_profile = group_profile.getObject("Demon_Profile")
        object_profile.changeParam('Accounts', slot_id_int, (slot_id_int, account_id))
        object_profile.setCurrent(account_id)

        # set previous difficulty settings
        for param, value in difficulty.items():
            Mengine.changeCurrentAccountSetting(param, value)

        for method in SystemChapterSelection.staticmethod_onCreateNewAccount:
            method(account_id)

        return False

    @staticmethod
    def addCbResetChapter(method):
        SystemChapterSelection.staticmethod_onCreateNewAccount.append(method)

    @staticmethod
    def __cbGameComplete():
        ChapterSelectionManager.setCurrentChapter(None)
        return False

    @staticmethod
    def __cbChapterOpen(chapter_id, value=True):
        chapter = SystemChapterSelection.getChapterSelection(chapter_id)
        chapter.setOpen(value)

        return False

    @staticmethod
    def __cbChapterBlock(chapter_id, value=True):
        chapter = SystemChapterSelection.getChapterSelection(chapter_id)
        chapter.setBlocked(value)

        return False

    def __cbChapterSelectionChoseChapter(self, value):
        param = ChapterSelectionManager.getChapterSelectionParam(value)
        chapter_selection = SystemChapterSelection.getChapterSelection(value)

        if self.existTaskChain("HandleChapterSelection"):
            self.removeTaskChain("HandleChapterSelection")

        with self.createTaskChain(Name="HandleChapterSelection") as tc:
            tc.addScope(self.__scopeHandleChapterSelected, param, chapter_selection)

        return False

    def __scopeHandleChapterSelected(self, source, param, chapter_selection):
        if param is None:
            ChapterSelectionManager.setCurrentChapter(None)
            return

        hasStage = StageManager.hasCurrentStage()
        semaphore_close_chapter_selection = SemaphoreManager.getSemaphore('CloseChapterSelection')

        if chapter_selection is not None:
            chapter_selection.setPlayed(True)

        SceneManager.setCurrentGameSceneName(param.start_scene)
        ChapterSelectionManager.setCurrentChapter(param.chapter_name)
        Map2Manager.setCurrentMap(param.map_demon_name)

        source.addSemaphore(semaphore_close_chapter_selection, From=True, To=False)  # wait until menu anim finish

        with source.addFork() as source_fork:
            # issue https://wonderland-games.atlassian.net/browse/HO2-266;
            # source_fork is bug fix for next repr (with accounts save enabled):
            # choose chapter,
            # on intro cutscene press altf4,
            # on next play we will be on empty cutscene scene,
            # but we should be on the param.start_scene scene
            # the main point of the fix is we need to
            # make sure after cutscene play we will execute SceneManager.setCurrentGameSceneName(param.start_scene)

            # how in actually should work:
            # this tc on game close should be skipped, and last task, AliasTransition should be skipped AND
            # on skip: set last scene as param.start_scene

            with source_fork.addRaceTask(2) as (race_0, race_1):
                race_0.addTask("TaskListener", ID=Notificator.onCutScenePlay)

                def __onTransitionEndFilter(sceneFrom, sceneTo, ZoomGroupName):
                    return sceneTo == "CutScene"
                race_1.addTask("TaskListener", ID=Notificator.onTransitionEnd, Filter=__onTransitionEndFilter)

            source_fork.addFunction(SceneManager.setCurrentGameSceneName, param.start_scene)  # actual fix  # source_fork.addPrint("SHITTY FIX IS IN FIRE BABY!!!")

        if param.start_paragraph is not None:
            source.addListener(Notificator.onSceneInit)
            source.addNotify(Notificator.onParagraphRun, param.start_paragraph)
        else:
            if param.start_cut_scene is not None:
                source.addTask("TaskCutScenePlay", CutSceneName=param.start_cut_scene, Transition=hasStage)
            source.addTask("AliasTransition", SceneName=param.start_scene)

    def _onStop(self):
        return

    @staticmethod
    def getChapterSelections():
        return SystemChapterSelection.s_chapter_selections

    @staticmethod
    def getChapterSelection(chapter_name):
        return SystemChapterSelection.s_chapter_selections.get(chapter_name)

    @staticmethod
    def _onSave():
        data_chapter_status = {}

        for param in SystemChapterSelection.getChapterSelections().values():
            data_chapter_status[param.chapter_name] = param.is_open, param.is_play_open_animation, param.is_played

        data_save = {'CurrentChapter': ChapterSelectionManager.s_chapter_current, 'ChapterStatus': data_chapter_status, }

        return data_save

    @staticmethod
    def _onLoad(data_save):
        for chapter_id, (open_status, open_anim_played, played) in data_save.get('ChapterStatus').iteritems():
            SystemChapterSelection.getChapterSelection(chapter_id).setOpen(open_status)
            SystemChapterSelection.getChapterSelection(chapter_id).setOpenAnimationPlayed(open_anim_played)
            SystemChapterSelection.getChapterSelection(chapter_id).setPlayed(played)

        chapter_name = data_save.get('CurrentChapter', None)
        ChapterSelectionManager.setCurrentChapter(chapter_name)

    # dev to debug integration

    def __addDevToDebug(self):
        if Mengine.isAvailablePlugin("DevToDebug") is False:
            return
        if SystemChapterSelection.s_dev_to_debug is True:
            return
        SystemChapterSelection.s_dev_to_debug = True

        tab = Mengine.getDevToDebugTab("Cheats") or Mengine.addDevToDebugTab("Cheats")

        w_bonus = Mengine.createDevToDebugWidgetButton("unlock_bonus_chapter")
        w_bonus.setTitle("Unlock Bonus Chapter")
        w_bonus.setClickEvent(Notification.notify, Notificator.onChapterOpen, "Bonus")

        tab.addWidget(w_bonus)