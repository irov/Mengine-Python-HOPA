from Foundation.DatabaseManager import DatabaseManager
from Foundation.DefaultManager import DefaultManager
from Foundation.SceneManager import SceneManager
from Foundation.System import System
from Foundation.TaskManager import TaskManager
from HOPA.ChapterManager import ChapterManager
from HOPA.QuestManager import QuestManager

class SystemDifficulty(System):

    def __init__(self):
        super(SystemDifficulty, self).__init__()
        self.scenarios = {}
        self.runners = []
        self.ScenariosDifficulty = None
        self.TutorialSkip = False

        self.bIsCustomDifficultySetOnce = False
        self.bSparkOnActiveArea = False
        self.bTutorialAvaliable = False
        self.bItemPlusIndicator = False
        self.bChangeActiveAreaIcon = False
        self.bMapIndicator = False
        self.bSparksOnHO = False
        self.fHintTime = 0.0
        self.fSkipTime = 0.0

    def _loadChapterDifficultyParam(self, module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            Difficulty = record.get("Difficulty")
            ScenarioID = record.get("ScenarioID")

            self.scenarios.setdefault(Difficulty, []).append(ScenarioID)

    def _onRun(self):
        CurrentChapterName = ChapterManager.getCurrentChapterName()

        if CurrentChapterName is not None:
            self._checkInjections(CurrentChapterName)
        else:
            self.addObserver(Notificator.onSetCurrentChapter, self._checkInjections)

        TutorialSkip = DefaultManager.getDefaultBool("TutorialSkip", False)

        if TutorialSkip is True:
            self.addObserver(Notificator.onTutorialSkipEnd, self._onTutorialSkip)

        return True

    def _onStop(self):
        if TaskManager.existTaskChain("Difficulty_TutorialCasual"):
            TaskManager.cancelTaskChain("Difficulty_TutorialCasual")

        self.ScenariosDifficulty = None

    def _onSave(self):
        # BAD PRACTICE!!! Do not use list or tuple for save!!
        return (self.ScenariosDifficulty, self.TutorialSkip, self.bIsCustomDifficultySetOnce, self.bSparkOnActiveArea, self.bTutorialAvaliable, self.bItemPlusIndicator, self.bChangeActiveAreaIcon, self.bMapIndicator, self.bSparksOnHO, self.fHintTime, self.fSkipTime)

    def _onLoad(self, data_save):
        self.ScenariosDifficulty, self.TutorialSkip = data_save[0], data_save[1]

        if len(data_save) > 2:
            self.bIsCustomDifficultySetOnce = data_save[2]

        if len(data_save) > 3:
            self.bSparkOnActiveArea = bool(data_save[3])
            self.bTutorialAvaliable = bool(data_save[4])
            self.bItemPlusIndicator = bool(data_save[5])
            self.bChangeActiveAreaIcon = bool(data_save[6])
            self.bMapIndicator = bool(data_save[7])
            self.bSparksOnHO = bool(data_save[8])

            self.fHintTime = float(data_save[9])
            self.fSkipTime = float(data_save[10])

    def isTutorialSkip(self):
        return self.TutorialSkip

    def _checkInjections(self, chapterName):
        ChapterModule, ChapterDifficulty = ChapterManager.getChapterDifficultyParam(chapterName)

        if ChapterDifficulty is None:
            return False

        self._loadChapterDifficultyParam(ChapterModule, ChapterDifficulty)

        if self.TutorialSkip is True:
            self._onTutorialSkip()

        if self.ScenariosDifficulty is not None:
            return True

        Difficulty = Mengine.getCurrentAccountSetting("Difficulty")
        FirstTutorialScene = DefaultManager.getDefault("FirstTutorialScene", None)

        with TaskManager.createTaskChain(Name="Difficulty_TutorialCasual") as tc:
            tc.addTask("TaskStageInit")

            if FirstTutorialScene is None:
                tc.addTask("TaskSceneActivate")
            else:
                tc.addTask("TaskSceneEnter", SceneName=FirstTutorialScene)

            if Difficulty == "Casual" or Difficulty == "Normal" or Difficulty == "" or Difficulty == "Custom":
                CHEAT_SKIP_MENU = DefaultManager.getDefaultBool("CHEAT_SKIP_MENU", False)
                PlayTutorialDefault = DefaultManager.getDefaultBool("PlayTutorial", True)
                PlayTutorialAccount = Mengine.getCurrentAccountSettingBool('DifficultyCustomTutorial')

                if any([PlayTutorialDefault is False, PlayTutorialAccount is False, CHEAT_SKIP_MENU is True]):
                    tc.addTask("TaskFunction", Fn=self._runScenarios, Args=(Difficulty,))
                else:
                    tc.addTask("TaskStateMutex", ID="AliasMessageShow", From=False)
                    tc.addTask("TaskStateChange", ID="AliasMessageShow", Value=True)

                    CurrentSceneName = SceneManager.getCurrentSceneName()
                    Fade = 0.5
                    Time = 0.25 * 1000.0

                    with tc.addParallelTask(2) as (tc_1, tc_2):
                        tutorial_text_id = DefaultManager.getDefault("DefaultWantTutorialTextID", "ID_WANTSHOWTUTORIAL")
                        tc_1.addTask("AliasMessageShow", TextID=tutorial_text_id)
                        tc_2.addTask("AliasFadeIn", FadeGroupName="FadeUI", To=Fade, Time=Time)

                    with tc.addRaceTask(2) as (tc_no, tc_yes):
                        tc_no.addTask("AliasMessageNo")

                        with tc_no.addParallelTask(2) as (tc_quit_1, tc_quit_2):
                            tc_quit_1.addTask("AliasMessageHide", SceneName=CurrentSceneName)
                            tc_quit_2.addTask("AliasFadeOut", FadeGroupName="FadeUI", Time=Time, From=Fade)

                        tc_no.addTask("TaskFunction", Fn=self._runScenarios, Args=(Difficulty,))
                        tc_no.addNotify(Notificator.onTutorialComplete)
                        #########################
                        tc_yes.addTask("AliasMessageYes")

                        with tc_yes.addParallelTask(2) as (tc_yes_1, tc_yes_2):
                            tc_yes_1.addTask("AliasMessageHide", SceneName=CurrentSceneName)
                            tc_yes_2.addTask("AliasFadeOut", FadeGroupName="FadeUI", Time=Time, From=Fade)

                        tc_yes.addTask("TaskFunction", Fn=self._runScenarios, Args=("Tutorial",))
                        tc_yes.addNotify(Notificator.onTutorial_Start)
                        tc_yes.addTask("TaskNotify", ID=Notificator.onMessage, Args=("DifficultyCasualSelect",))

                    tc.addTask("TaskStateChange", ID="AliasMessageShow", Value=False)
            else:
                tc.addTask("TaskFunction", Fn=self._runScenarios, Args=("Expert",))

        return False

    def _onTutorialSkip(self):
        scenarios = self.scenarios[self.ScenariosDifficulty]

        currentScenarioChapter = ChapterManager.getCurrentChapter()

        for scenarioID in scenarios:
            currentScenarioChapter.skipInjection(scenarioID)

            runner = currentScenarioChapter.getScenario(scenarioID)
            if runner is None:  # if already skipped, than it will be none on next load
                continue

            runner.stop()

            # need to remove quests in memory OR to reload chapters))). first way is better))
            def questVisitor(quest):
                QuestManager.completeQuest(quest, True)  # complete=True

            runner_scenario = runner.getScenario()
            runner_paragraphs = runner_scenario.getParagraphs()
            runner_repeats = runner_scenario.getRepeats()

            for scenario_commands in runner_paragraphs + runner_repeats:
                scenario_commands.visitQuests(questVisitor, False)  # brake=False

        self.TutorialSkip = True

        return False

    def _runScenarios(self, Difficulty):
        self.ScenariosDifficulty = Difficulty

        if self.ScenariosDifficulty not in self.scenarios.keys():
            # print "WARNING!!!! SystemDifficulty not have scenarios for difficulty '%s', need add xls!"%(self.ScenariosDifficulty)
            return

        scenarios = self.scenarios[self.ScenariosDifficulty]

        currentScenarioChapter = ChapterManager.getCurrentChapter()

        for scenarioID in scenarios:
            runner = ChapterManager.chapterAddRunInjection(currentScenarioChapter, scenarioID)
            self.runners.append(runner)