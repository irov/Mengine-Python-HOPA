from Foundation.DefaultManager import DefaultManager
from Foundation.GroupManager import GroupManager
from Foundation.GuardBlockInput import GuardBlockInput
from Foundation.SceneManager import SceneManager
from Foundation.System import System
from Foundation.TaskManager import TaskManager
from HOPA.ChapterSelectionManager import ChapterSelectionManager
from HOPA.CutSceneManager import CutSceneManager
from HOPA.DialogManager import DialogManager
from HOPA.Entities.Difficulty2.Difficulty2Manager import Difficulty2Manager
from HOPA.Entities.Map2.Map2Manager import Map2Manager
from HOPA.StageManager import StageManager


class SystemFastStart(System):

    @staticmethod
    def hasChapterSelection():
        if len(ChapterSelectionManager.s_chapter_selection_params) == 0:
            return False
        # SystemManager.hasSystem returns False, because this system is Global and runs first
        # then starts SystemChapterSelection. So when we do `hasSystem` - it not imported yet
        return True

    @staticmethod
    def hasFastStartAppArgs():
        cutscene_id = Mengine.getOptionValue("cutscene")
        if cutscene_id != "":
            if CutSceneManager.hasScene(cutscene_id) is False:
                Trace.log("System", 0, "Can't do fast start: not found CutSceneID {!r}".format(cutscene_id))
                return False

        dialog_id = Mengine.getOptionValue("dialog")
        if dialog_id != "":
            if DialogManager.hasDialog(dialog_id) is False:
                Trace.log("System", 0, "Can't do fast start: not found DialogID {!r}".format(dialog_id))
                return False

        scene = Mengine.getOptionValue("scene")
        zoom = Mengine.getOptionValue("zoom")

        if scene != "":
            scenes = SceneManager.getScenes()
            if scene not in scenes:
                Trace.log("System", 0, "Can't do fast start, not found scene '%s' please add valid scene with -scene:{sceneName} template" % scene)
                return False

        return any([scene != "", zoom != "", cutscene_id != "", dialog_id != ""])

    @staticmethod
    def _parseFastStartAppArgs():
        """
        parse -chapter:{chapter_name} -scene:{scene_name}
            -zoom:{zoom_name} -cutscene:{cutscene_id} -dialog:{dialog_id}
        auto handle chapter if none
        if zoom is valid -> auto handle scene
        if cutscene - first play cutscene, then transit to -scene or menu
        """
        ChapterName = Mengine.getOptionValue("chapter")
        if ChapterName == "":
            ChapterName = None

        SceneName = Mengine.getOptionValue("scene")
        if SceneName == "":
            SceneName = None

        ZoomGroupName = Mengine.getOptionValue("zoom")
        if ZoomGroupName == "":
            ZoomGroupName = None

        # override sceneName
        if ZoomGroupName:
            ZoomSceneName = SceneManager.findZoomMainScene(ZoomGroupName)
            if ZoomSceneName:
                SceneName = ZoomSceneName

        # find chapter param
        ChapterParam = None
        if SystemFastStart.hasChapterSelection():
            ChapterParam = ChapterSelectionManager.getChapterSelectionParam(ChapterName)
            if ChapterParam is None:
                ChapterParam = ChapterSelectionManager.getParamByChaptersAnyScene(SceneName)
                if ChapterParam is None:
                    ChapterParam = ChapterSelectionManager.getFirstValidParam()

        CutSceneID = Mengine.getOptionValue("cutscene")
        if CutSceneID == "":
            CutSceneID = None

        DialogID = Mengine.getOptionValue("dialog")
        if DialogID == "":
            DialogID = None

        if (CutSceneID is not None or DialogID is not None) and SceneName is None:
            # if no -scene, but -cutscene or -dialog, then transit user to Menu after CutScene or Dialog
            SceneName = "Menu"

        return ChapterParam, SceneName, ZoomGroupName, CutSceneID, DialogID

    def _onRun(self):
        if not _DEVELOPMENT:
            return True

        if not self.hasFastStartAppArgs():
            return True

        bHasChapterSelection = self.hasChapterSelection()

        ChapterParam, SceneName, ZoomGroupName, CutSceneID, DialogID = self._parseFastStartAppArgs()

        if SceneName is None:
            SceneName = Mengine.getOptionValue("scene")
            Trace.log("System", 0, "Can't do fast start, not found scene '%s' please add valid scene with -scene:{sceneName} template" % SceneName)

        if bHasChapterSelection and ChapterParam is None:
            Trace.log("System", 0, "Can't auto handle chapter for scene %s please add chapter name with -chapter:{chapterName} template" % SceneName)

        def __handleFastStart(source):
            if StageManager.hasCurrentStage() is False:
                source.addTask("TaskStageRun", StageName=DefaultManager.getDefault("StartStage", "StageFX1"))

                if bHasChapterSelection:
                    source.addFunction(ChapterSelectionManager.setCurrentChapter, ChapterParam.chapter_name)
                    source.addFunction(Map2Manager.setCurrentMap, ChapterParam.map_demon_name)

            source.addFunction(self._setupDifficulty)
            if CutSceneID is not None:
                source.addTask("TaskCutScenePlay", CutSceneName=CutSceneID, Transition=True)
            if DialogID is not None:
                source.addTask('AliasTransition', SceneName="Dialog")
                source.addTask("TaskSceneInit", SceneName="Dialog")
                source.addTask("AliasDialogPlay", DialogID=DialogID)
            source.addTask('AliasTransition', SceneName=SceneName, ZoomGroupName=ZoomGroupName, IgnoreGameScene=True)

        with TaskManager.createTaskChain() as tc:
            with GuardBlockInput(tc) as guard_source:
                guard_source.addTask("TaskListener", ID=Notificator.onLoadAccounts)
                guard_source.addFunction(self.__handleAccountSelection)

                guard_source.addTask("TaskNotify", ID=Notificator.onLoadSession)
            tc.addScope(__handleFastStart)

        return True

    def _setupVolume(self):
        musicValue = DefaultManager.getDefaultFloat("DefaultMusicVolume", 0.5)
        Mengine.changeCurrentAccountSetting("MusicVolume", unicode(musicValue))

        soundValue = DefaultManager.getDefaultFloat("DefaultSoundVolume", 0.5)
        Mengine.changeCurrentAccountSetting("SoundVolume", unicode(soundValue))

        voiceValue = DefaultManager.getDefaultFloat("DefaultVoiceVolume", 0.5)
        Mengine.changeCurrentAccountSetting("VoiceVolume", unicode(voiceValue))

    def _setupDifficulty(self):
        if Mengine.hasCurrentAccount() is False:
            Trace.msg_err("SystemFastStart can't setup difficulty - no account selected.")
            return

        DIFFICULTY_PARAMS = {ID: params for ID, params in Difficulty2Manager.s_difficultiesSettings.items()}
        cur_difficulty = DIFFICULTY_PARAMS.get(Mengine.getOptionValue("fastdif").title() or "Casual")

        if cur_difficulty is None:
            if len(DIFFICULTY_PARAMS) == 0:
                Trace.log("System", 0, "SystemFastStart can't setup difficulty params, "
                                       "coz no difficulty params setup in game at all (add it to Difficulty2.xlsx)")
                return
            first_dif_id = DIFFICULTY_PARAMS.keys()[0]
            cur_difficulty = DIFFICULTY_PARAMS.get(first_dif_id)
            Trace.msg_err("SystemFastStart tried to setup difficulty 'Casual', "
                          "but it not found in DatabaseDifficulty2, so we used {!r}".format(first_dif_id))

        SETTINGS = {
            "DifficultyCustomHintTime": "HintTime",
            "DifficultyCustomSkipTime": "SkipTime",
            "DifficultyCustomSparklesOnActiveAreas": "SparklesOnActiveAreas",
            "DifficultyCustomTutorial": "Tutorial",
            "DifficultyCustomPlusItemIndicated": "PlusItemIndicated",
            "DifficultyCustomChangeIconOnActiveAreas": "ChangeIconOnActiveAreas",
            "DifficultyCustomIndicatorsOnMap": "IndicatorsOnMap",
            "DifficultyCustomSparklesOnHOPuzzles": "SparklesOnHOPuzzles",
            "Difficulty": "ID"
        }

        for account_param_name, dif_param_name in SETTINGS.items():
            option = cur_difficulty.get(dif_param_name)
            if option is None:
                continue
            if dif_param_name in ["HintTime", "SkipTime"]:
                option *= 1000.0  # ms
            elif account_param_name != "Difficulty":
                option = bool(option)
            Mengine.changeCurrentAccountSetting(account_param_name, unicode(option))
            # print "[{}]".format(cur_difficulty["ID"]), "changeCurrentAccountSetting", account_param_name, unicode(option)

        Trace.msg("SystemFastStart set difficulty to {!r}".format(cur_difficulty["ID"]))

    def __handleAccountSelection(self):
        Demon_Profile = GroupManager.getObject("Profile", "Demon_Profile")

        # ---------- debug:
        # print "HAS CURRENT MENGINE ACCOUNT : ", Mengine.hasCurrentAccount()
        # print "ACCOUNTS ", Mengine.getAccounts()
        # print "DEMON CUR ", Demon_Profile.getParam("Current")

        if Demon_Profile.getParam("Current") is None or Mengine.getCurrentAccountSettingBool("Default") is True:
            account_id = self.__createFastAccount()
            self.__selectAccount(account_id)

    def __createFastAccount(self):
        account_id = Mengine.createAccount()

        Mengine.changeAccountSetting(account_id, "SlotID", unicode(0))
        Mengine.changeAccountSetting(account_id, "Name", unicode("SystemFastStart"))
        Mengine.changeAccountSetting(account_id, "SessionSave", unicode(False))
        Mengine.changeAccountSetting(account_id, "Default", unicode(False))

        Demon_Profile = GroupManager.getObject("Profile", "Demon_Profile")
        Demon_Profile.appendParam("Accounts", (0, account_id))

        Demon_ProfileNew = GroupManager.getObject("Profile_New", "Demon_ProfileNew")
        Demon_ProfileNew.setAccountID(account_id)

        Notification.notify(Notificator.onCreateNewProfile, 0)
        # Trace.msg("<SystemFastStart> account created | id={!r}".format(account_id))

        return account_id

    def __selectAccount(self, account_id):
        def __apply_settings():
            demon_profile = GroupManager.getObject("Profile", "Demon_Profile")
            demon_profile.setParam("Current", account_id)
            self._setupVolume()

        with self.createTaskChain(Name="FastSelectAccount") as tc:
            tc.addFunction(Mengine.selectAccount, account_id)
            tc.addFunction(__apply_settings)
            tc.addFunction(Mengine.saveAccounts)
