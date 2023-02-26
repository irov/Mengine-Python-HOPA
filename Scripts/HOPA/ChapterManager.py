from Foundation.DatabaseManager import DatabaseManager
from Foundation.SceneManager import SceneManager
from HOPA.ScenarioChapter import ScenarioChapter
from HOPA.ScenarioManager import ScenarioManager

class ChapterManager(object):
    s_chapterScenarios = {}
    s_currentChapter = None
    s_currentChapterName = None
    s_chapterDifficulty = {}

    @staticmethod
    def onInitialize():
        pass

    @staticmethod
    def onFinalize():
        pass

    @staticmethod
    def setCurrentChapter(scenarioChapter):
        ChapterManager.s_currentChapter = scenarioChapter
        pass

    @staticmethod
    def setCurrentChapterName(chapterName):
        ChapterManager.s_currentChapterName = chapterName
        pass

    @staticmethod
    def getCurrentChapter():
        return ChapterManager.s_currentChapter
        pass

    @staticmethod
    def getCurrentChapterName():
        return ChapterManager.s_currentChapterName
        pass

    @staticmethod
    def getChapterDifficultyParam(chapterName):
        if chapterName not in ChapterManager.s_chapterDifficulty.keys():
            return None
            pass

        return ChapterManager.s_chapterDifficulty[chapterName]
        pass

    @staticmethod
    def loadParams(module, param):
        if param == "Chapter1":
            ChapterManager.loadChapterScenarios(module, "Chapter1", "Chapter1")
            pass
        if param == "Chapter2":
            ChapterManager.loadChapterScenarios(module, "Chapter2", "Chapter2")
            pass
        if param == "Chapter3":
            ChapterManager.loadChapterScenarios(module, "Chapter3", "Chapter3")
            pass
        if param == "Chapter4":
            ChapterManager.loadChapterScenarios(module, "Chapter4", "Chapter4")
            pass
        if param == "Chapter5":
            ChapterManager.loadChapterScenarios(module, "Chapter5", "Chapter5")
            pass
        if param == "Chapter6":
            ChapterManager.loadChapterScenarios(module, "Chapter6", "Chapter6")
            pass
        if param == "Chapter7":
            ChapterManager.loadChapterScenarios(module, "Chapter7", "Chapter7")
            pass
        if param == "Chapter8":
            ChapterManager.loadChapterScenarios(module, "Chapter8", "Chapter8")
            pass
        if param == "DifficultyChapters":
            ChapterManager.loadChapterDifficulty(module, "DifficultyChapters")
            pass

        return True
        pass

    @staticmethod
    def loadChapterScenarios(module, chapterName, param):
        records = DatabaseManager.getDatabaseRecords(module, param)
        ChapterManager.s_chapterScenarios[chapterName] = []

        for record in records:
            ScenarioID = record.get("ScenarioID")
            ChapterManager.s_chapterScenarios[chapterName].append(ScenarioID)
            pass
        pass

    @staticmethod
    def loadChapterDifficulty(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            ChapterName = record.get("ChapterName")
            Param = record.get("Param")

            ChapterManager.s_chapterDifficulty[ChapterName] = (module, Param)
            pass
        pass

    @staticmethod
    def getChapterScenarios(chapterName):
        return ChapterManager.s_chapterScenarios[chapterName]
        pass

    @staticmethod
    def generateChapterScenarios(chapterName):
        if chapterName not in ChapterManager.s_chapterScenarios:
            Trace.log("Manager", 0, "ChapterManager.generateChapterScenarios not found chapter %s" % (chapterName))

            return None
            pass

        scenarioChapter = ScenarioChapter()

        ChapterScenarioIDs = ChapterManager.getChapterScenarios(chapterName)

        for ScenarioID in ChapterScenarioIDs:
            if isinstance(ScenarioManager.getScenario(ScenarioID), ScenarioManager.EmptyScenario):
                continue

            Runner = ScenarioManager.generateScenario(ScenarioID)

            if Runner is None:
                Trace.log("Manager", 0, "ChapterManager.generateChapterScenarios invalid generate scenario %s" % (ScenarioID))

                return None
                pass

            scenarioChapter.addScenario(ScenarioID, Runner)
            pass

        if scenarioChapter.onInitialize() is False:
            Trace.log("Manager", 0, "ChapterManager.generateChapterScenarios '%s' invalid initialize scenario chapter" % (chapterName))
            return None
            pass

        return scenarioChapter
        pass

    @staticmethod
    def chapterAddRunInjection(ScenarioChapter, ScenarioID):
        Runner = ChapterManager.chapterAddInjection(ScenarioChapter, ScenarioID)

        if Runner is None:
            return None
            pass

        Runner.onInitialize()
        Runner.generateScenario(ScenarioChapter)
        Runner.run()

        return Runner
        pass

    @staticmethod
    def chapterAddRunNotSaveInjection(ScenarioChapter, ScenarioID):
        Runner = ChapterManager.chapterAddNotSaveInjection(ScenarioChapter, ScenarioID)

        Runner.onInitialize()
        Runner.generateScenario(ScenarioChapter)
        Runner.run()

        return Runner
        pass

    @staticmethod
    def chapterAddInjection(ScenarioChapter, ScenarioID):
        Runner = ScenarioManager.generateScenario(ScenarioID)

        if Runner is None:
            Trace.log("Manager", 0, "ChapterManager.chapterAddInjection invalid generate scenario %s" % (ScenarioID))

            return None
            pass

        ScenarioChapter.addScenario(ScenarioID, Runner)

        return Runner
        pass

    @staticmethod
    def chapterAddNotSaveInjection(ScenarioChapter, ScenarioID):
        Runner = ScenarioManager.generateScenario(ScenarioID)

        return Runner
        pass

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
                pass

            Groups.append(GroupName)
            pass

        return Groups
        pass

    @staticmethod
    def findCurrentChapterGameScenes():
        curChapterName = ChapterManager.getCurrentChapterName()

        Scenes = []

        ChapterScenarioIDs = ChapterManager.s_chapterScenarios[curChapterName]
        for ScenarioID in ChapterScenarioIDs:
            SceneName = ScenarioManager.getScenarioGroupName(ScenarioID)
            if SceneName in Scenes:
                continue
                pass
            if SceneManager.isGameScene(SceneName) is False:
                continue
                pass
            Scenes.append(SceneName)
            pass

        return Scenes
        pass

    @staticmethod
    def findCurrentChapterScenes():
        curChapterName = ChapterManager.getCurrentChapterName()

        Scenes = []

        ChapterScenarioIDs = ChapterManager.s_chapterScenarios[curChapterName]
        for ScenarioID in ChapterScenarioIDs:
            SceneName = ScenarioManager.getScenarioGroupName(ScenarioID)
            if SceneName in Scenes:
                continue
                pass
                # if SceneManager.isGameScene(SceneName) is False:
                #     continue
                pass
            Scenes.append(SceneName)
            pass

        return Scenes
        pass

    pass