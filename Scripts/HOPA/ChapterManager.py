from Foundation.Manager import Manager

from Foundation.DatabaseManager import DatabaseManager
from Foundation.SceneManager import SceneManager
from HOPA.ScenarioChapter import ScenarioChapter
from HOPA.ScenarioManager import ScenarioManager

class ChapterManager(Manager):
    s_chapterScenarios = {}
    s_currentChapter = None
    s_currentChapterName = None
    s_chapterDifficulty = {}

    @staticmethod
    def _onInitialize():
        pass

    @staticmethod
    def _onFinalize():
        ChapterManager.s_chapterScenarios = {}
        ChapterManager.s_currentChapter = None
        ChapterManager.s_currentChapterName = None
        ChapterManager.s_chapterDifficulty = {}
        pass

    @staticmethod
    def setCurrentChapter(scenarioChapter):
        ChapterManager.s_currentChapter = scenarioChapter

    @staticmethod
    def setCurrentChapterName(chapterName):
        ChapterManager.s_currentChapterName = chapterName

    @staticmethod
    def getCurrentChapter():
        return ChapterManager.s_currentChapter

    @staticmethod
    def getCurrentChapterName():
        return ChapterManager.s_currentChapterName

    @staticmethod
    def getChapterDifficultyParam(chapterName):
        if chapterName not in ChapterManager.s_chapterDifficulty.keys():
            return None
        return ChapterManager.s_chapterDifficulty[chapterName]

    @staticmethod
    def loadParams(module, param):
        if param == "DifficultyChapters":
            ChapterManager.loadChapterDifficulty(module, "DifficultyChapters")
        elif param.startswith("Chapter"):
            ChapterManager.loadChapterScenarios(module, param, param)
        else:
            if _DEVELOPMENT is True:
                Trace.log("Manager", 0, "Not found handler for {}".format(param))
        return True

    @staticmethod
    def loadChapterScenarios(module, chapterName, param):
        records = DatabaseManager.getDatabaseRecords(module, param)
        ChapterManager.s_chapterScenarios[chapterName] = []

        for record in records:
            ScenarioID = record.get("ScenarioID")
            ChapterManager.s_chapterScenarios[chapterName].append(ScenarioID)

    @staticmethod
    def loadChapterDifficulty(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            ChapterName = record.get("ChapterName")
            Param = record.get("Param")

            ChapterManager.s_chapterDifficulty[ChapterName] = (module, Param)

    @staticmethod
    def getChapterScenarios(chapterName):
        return ChapterManager.s_chapterScenarios[chapterName]

    @staticmethod
    def generateChapterScenarios(chapterName):
        if chapterName not in ChapterManager.s_chapterScenarios:
            Trace.log("Manager", 0, "ChapterManager.generateChapterScenarios not found chapter %s" % (chapterName))
            return None

        scenarioChapter = ScenarioChapter()

        ChapterScenarioIDs = ChapterManager.getChapterScenarios(chapterName)

        for ScenarioID in ChapterScenarioIDs:
            if isinstance(ScenarioManager.getScenario(ScenarioID), ScenarioManager.EmptyScenario):
                continue

            Runner = ScenarioManager.generateScenario(ScenarioID)

            if Runner is None:
                Trace.log("Manager", 0, "ChapterManager.generateChapterScenarios invalid generate scenario %s" % (ScenarioID))
                return None

            scenarioChapter.addScenario(ScenarioID, Runner)

        if scenarioChapter.onInitialize() is False:
            Trace.log("Manager", 0, "ChapterManager.generateChapterScenarios '%s' invalid initialize scenario chapter" % (chapterName))
            return None

        return scenarioChapter

    @staticmethod
    def chapterAddRunInjection(ScenarioChapter, ScenarioID):
        Runner = ChapterManager.chapterAddInjection(ScenarioChapter, ScenarioID)

        if Runner is None:
            return None

        Runner.onInitialize()
        Runner.generateScenario(ScenarioChapter)
        Runner.run()

        return Runner

    @staticmethod
    def chapterAddRunNotSaveInjection(ScenarioChapter, ScenarioID):
        Runner = ChapterManager.chapterAddNotSaveInjection(ScenarioChapter, ScenarioID)

        Runner.onInitialize()
        Runner.generateScenario(ScenarioChapter)
        Runner.run()

        return Runner

    @staticmethod
    def chapterAddInjection(ScenarioChapter, ScenarioID):
        Runner = ScenarioManager.generateScenario(ScenarioID)

        if Runner is None:
            Trace.log("Manager", 0, "ChapterManager.chapterAddInjection invalid generate scenario %s" % (ScenarioID))
            return None

        ScenarioChapter.addScenario(ScenarioID, Runner)
        return Runner

    @staticmethod
    def chapterAddNotSaveInjection(ScenarioChapter, ScenarioID):
        Runner = ScenarioManager.generateScenario(ScenarioID)
        return Runner

    @staticmethod
    def getChapterGroups(chapterName):
        if chapterName not in ChapterManager.s_chapterScenarios:
            return None
            pass

        Groups = []
        ChapterScenarioIDs = ChapterManager.s_chapterScenarios[chapterName]
        for ScenarioID in ChapterScenarioIDs:
            GroupName = ScenarioManager.getScenarioGroupName(ScenarioID)
            if GroupName in Groups:
                continue
            Groups.append(GroupName)

        return Groups

    @staticmethod
    def findCurrentChapterGameScenes():
        curChapterName = ChapterManager.getCurrentChapterName()

        Scenes = []

        ChapterScenarioIDs = ChapterManager.s_chapterScenarios[curChapterName]
        for ScenarioID in ChapterScenarioIDs:
            SceneName = ScenarioManager.getScenarioGroupName(ScenarioID)
            if SceneName in Scenes:
                continue
            if SceneManager.isGameScene(SceneName) is False:
                continue
            Scenes.append(SceneName)

        return Scenes

    @staticmethod
    def findCurrentChapterScenes():
        curChapterName = ChapterManager.getCurrentChapterName()

        Scenes = []

        ChapterScenarioIDs = ChapterManager.s_chapterScenarios[curChapterName]
        for ScenarioID in ChapterScenarioIDs:
            SceneName = ScenarioManager.getScenarioGroupName(ScenarioID)
            if SceneName in Scenes:
                continue
            Scenes.append(SceneName)

        return Scenes
