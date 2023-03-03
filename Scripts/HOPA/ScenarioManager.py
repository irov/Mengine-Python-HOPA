from Foundation.Bootstrapper import checkBuildMode
from Foundation.DatabaseManager import DatabaseManager
from Foundation.SceneManager import SceneManager
from HOPA.ScenarioChapter import ScenarioChapter
from HOPA.ScenarioRunner import ScenarioRunner
from Notification import Notification


class ScenarioManager(object):
    class EmptyScenario(object):
        def __init__(self):
            pass

    s_scenarioType = {}
    s_scenarios = {}
    s_runScenarios = {}

    Scenario_Init = []
    Scenario_Enter = []
    onScenarioInit = None
    onScenarioEnter = None
    onScenarioLeave = None
    onSceneRemoved = None

    class ScenarioDesc(object):
        def __init__(self, SceneName, ZoomName, Module, ScenarioName, PlusName):
            self.SceneName = SceneName
            self.ZoomName = ZoomName
            self.Module = Module
            self.ScenarioName = ScenarioName
            self.PlusName = PlusName

    @staticmethod
    def onInitialize():
        ScenarioManager.onScenarioInit = Notification.addObserver(Notificator.onScenarioInit, ScenarioManager.__onScenarioInit)
        ScenarioManager.onScenarioEnter = Notification.addObserver(Notificator.onScenarioEnter, ScenarioManager.__onScenarioEnter)
        ScenarioManager.onScenarioLeave = Notification.addObserver(Notificator.onScenarioLeave, ScenarioManager.__onScenarioLeave)
        ScenarioManager.onSceneRemoved = Notification.addObserver(Notificator.onSceneRemoved, ScenarioManager.__onSceneRemoved)
        pass

    @staticmethod
    def onFinalize():
        Notification.removeObserver(ScenarioManager.onScenarioInit)
        Notification.removeObserver(ScenarioManager.onScenarioEnter)
        Notification.removeObserver(ScenarioManager.onScenarioLeave)
        Notification.removeObserver(ScenarioManager.onSceneRemoved)
        pass

    @staticmethod
    def __onScenarioInit(Scenario_Id):
        if Scenario_Id not in ScenarioManager.Scenario_Init:
            ScenarioManager.Scenario_Init.append(Scenario_Id)
            pass

        return False
        pass

    @staticmethod
    def __onScenarioEnter(Scenario_Id):
        if Scenario_Id not in ScenarioManager.Scenario_Enter:
            ScenarioManager.Scenario_Enter.append(Scenario_Id)
            pass

        return False
        pass

    @staticmethod
    def __onScenarioLeave(Scenario_Id):
        if Scenario_Id in ScenarioManager.Scenario_Enter:
            for i in range(len(ScenarioManager.Scenario_Enter)):
                if ScenarioManager.Scenario_Enter[i] == Scenario_Id:
                    del ScenarioManager.Scenario_Enter[i]
                    break
                    pass
                pass
            pass

        return False
        pass

    @staticmethod
    def __onSceneRemoved(SceneName):
        GroupName = SceneManager.getSceneMainGroupName(SceneName)
        Scenarios = ScenarioManager.getSceneRunScenarios(SceneName, GroupName)

        for ScenarioRunner in Scenarios:
            ScenarioRunner.skip()
            pass

        return False
        pass

    @staticmethod
    def isScenarioInit(Scenario_Id):
        return Scenario_Id in ScenarioManager.Scenario_Init
        pass

    @staticmethod
    def isScenarioEnter(Scenario_Id):
        return Scenario_Id in ScenarioManager.Scenario_Enter
        pass

    @staticmethod
    def addScenario(ScenarioID, SceneName, ZoomName, Module, ScenarioName, PlusName, Survey, CE, BuildModeTags):
        if checkBuildMode(ScenarioID, Survey, CE, BuildModeTags) is True:
            ScenarioManager.s_scenarios[ScenarioID] = ScenarioManager.EmptyScenario()
            return True

        if ZoomName is not None:
            from HOPA.ZoomManager import ZoomManager

            if ZoomManager.hasZoom(ZoomName) is False:
                Trace.log("Manager", 0, "ScenarioManager.loadScenarios: zoom [%s] not found" % (ZoomName))
                return False

        desc = ScenarioManager.ScenarioDesc(SceneName, ZoomName, Module, ScenarioName, PlusName)

        ScenarioManager.s_scenarios[ScenarioID] = desc
        pass

    @staticmethod
    def getScenario(id):
        if id not in ScenarioManager.s_scenarios:
            Trace.log("Manager", 0, "ScenarioManager.getScenario not found scenario %s" % (id))

            return None
            pass

        scenario = ScenarioManager.s_scenarios[id]

        return scenario
        pass

    @staticmethod
    def hasScenario(id):
        return id in ScenarioManager.s_scenarios
        pass

    @staticmethod
    def getScenarioIdBySceneName(SceneName):
        for key, val in ScenarioManager.s_scenarios.iteritems():
            if isinstance(val, ScenarioManager.EmptyScenario):
                continue
            if (SceneName == val.SceneName):
                return key
                pass
            pass
        return None
        pass

    @staticmethod
    def getScenarioIdsBySceneName(SceneName):
        scenarios = []
        for key, val in ScenarioManager.s_scenarios.iteritems():
            if isinstance(val, ScenarioManager.EmptyScenario):
                continue
            if (SceneName == val.SceneName):
                scenarios.append(key)
                pass
            pass
        return scenarios
        pass

    @staticmethod
    def getScenarioIdBySceneName2(SceneName, ZoomName=None):
        for key, val in ScenarioManager.s_scenarios.iteritems():
            if isinstance(val, ScenarioManager.EmptyScenario):
                continue
            if (SceneName == val.SceneName) and (ZoomName == val.ZoomName):
                return key
                pass
            pass
        return None
        pass

    @staticmethod
    def getScenarioIdsBySceneName2(SceneName, ZoomName=None):
        scenarios = []
        for key, val in ScenarioManager.s_scenarios.iteritems():
            if isinstance(val, ScenarioManager.EmptyScenario):
                continue
            if SceneName == val.SceneName and ZoomName == val.ZoomName:
                scenarios.append(key)
                pass
            pass

        return scenarios
        pass

    @staticmethod
    def getSceneRunScenarios(SceneName, GroupName):
        from HOPA.ChapterManager import ChapterManager

        RunSceneScenarios = []
        for ScenarioChapter in ScenarioManager.s_runScenarios.itervalues():
            scenarios = ScenarioChapter.findSceneGroupScenarios(SceneName, GroupName)
            for Scenario in scenarios:
                if Scenario.SceneName == SceneName and Scenario.GroupName == GroupName:
                    RunSceneScenarios.append(Scenario)
                    pass
                pass
            pass

        currentChapter = ChapterManager.getCurrentChapter()

        if currentChapter is None:
            return RunSceneScenarios
            pass

        ChapterScenarios = currentChapter.findSceneGroupScenarios(SceneName, GroupName)

        SceneScenarios = RunSceneScenarios + ChapterScenarios

        return SceneScenarios
        pass

    @staticmethod
    def importScenario(module, name):
        Name = "Scenario%s" % (name)
        FromName = module
        ModuleName = "%s.%s" % (FromName, Name)
        Module = __import__(ModuleName, fromlist=[FromName])
        ScenarioType = getattr(Module, Name)

        return ScenarioType
        pass

    @staticmethod
    def getScenarioType(module, name):
        path = (module, name)

        if path in ScenarioManager.s_scenarioType:
            return ScenarioManager.s_scenarioType[path]
            pass

        ScenarioType = ScenarioManager.importScenario(module, name)

        ScenarioManager.s_scenarioType[path] = ScenarioType

        return ScenarioType
        pass

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            ScenarioID = record.get("ScenarioID")
            SceneName = record.get("SceneName")
            if SceneManager.hasScene(SceneName) is False:
                Trace.log("Manager", 0, "ScenarioManager.loadScenarios: scene [%s] not found" % (SceneName))
                return False
                pass

            ZoomName = record.get("ZoomName")
            Module = record.get("Module")
            ScenarioName = record.get("Scenario")
            PlusName = record.get("PlusName", None)
            Survey = int(record.get("Survey", 0))
            CE = int(record.get("CE", 0))
            BuildModeTags = record.get("BuildModeTags", [])

            ScenarioManager.addScenario(ScenarioID, SceneName, ZoomName, Module, ScenarioName, PlusName, Survey, CE, BuildModeTags)
            pass

        return True
        pass

    @staticmethod
    def createScenario(scenarioID):
        Runner = ScenarioManager.generateScenario(scenarioID)

        if Runner is None:
            Trace.log("Manager", 0, "ChapterManager.createScenario invalid generate scenario %s" % (scenarioID))

            return None
            pass

        Chapter = ScenarioChapter()

        Chapter.addScenario(scenarioID, Runner)

        if Chapter.onInitialize() is False:
            Trace.log("Manager", 0, "ChapterManager.createScenario '%s' invalid initialize scenario chapter" % (scenarioID))

            return None
            pass

        return Chapter
        pass

    @staticmethod
    def addRunScenario(scenarioID, scenarioChapter):
        ScenarioManager.s_runScenarios[scenarioID] = scenarioChapter
        pass

    @staticmethod
    def runScenario(scenarioID):
        scenarioChapter = ScenarioManager.createScenario(scenarioID)
        scenarioChapter.run()

        ScenarioManager.addRunScenario(scenarioID, scenarioChapter)
        return scenarioChapter
        pass

    @staticmethod
    def runScenarioOptions(scenarioID, **kwg):
        scenarioChapter = ScenarioManager.createScenario(scenarioID)
        scenarioChapter.setOptions(kwg)
        scenarioChapter.run()

        ScenarioManager.addRunScenario(scenarioID, scenarioChapter)
        return scenarioChapter
        pass

    @staticmethod
    def cancelScenario(scenarioID):
        if scenarioID not in ScenarioManager.s_runScenarios.keys():
            Trace.log("Manager", 0, "ScenarioManager runScenario error, %s not run" % (scenarioID))
            return
            pass

        scenarioRunner = ScenarioManager.s_runScenarios.pop(scenarioID)
        scenarioRunner.stop()
        pass

    @staticmethod
    def skipScenario(scenarioID):
        from HOPA.ChapterManager import ChapterManager
        scenarioChapter = ChapterManager.getCurrentChapter()

        scenarioChapter.skipScenario(scenarioID)
        pass

    @staticmethod
    def generateScenario(ScenarioID):
        if ScenarioManager.hasScenario(ScenarioID) is False:
            Trace.log("Manager", 0, "ScenarioManager.generateScenario not found scenario %s" % (ScenarioID))
            return None
            pass

        ScenarioDesc = ScenarioManager.getScenario(ScenarioID)

        if isinstance(ScenarioDesc, ScenarioManager.EmptyScenario):
            return None

        SceneName = ScenarioDesc.SceneName

        isZoom = ScenarioDesc.ZoomName is not None

        isPlusScene = ScenarioDesc.PlusName is not None

        if isZoom is True:
            GroupName = ScenarioDesc.ZoomName
        else:
            GroupName = SceneManager.getSceneMainGroupName(ScenarioDesc.SceneName)
            pass

        ScenarioType = ScenarioManager.getScenarioType(ScenarioDesc.Module, ScenarioDesc.ScenarioName)

        Scenario = ScenarioType()

        Scenario.onInitialize(GroupName, SceneName, ScenarioID)

        Runner = ScenarioRunner(ScenarioDesc.ScenarioName, ScenarioDesc.SceneName, GroupName, isZoom, Scenario, isPlusScene)

        return Runner
        pass

    @staticmethod
    def getScenarioGroupName(ScenarioID):
        if isinstance(ScenarioManager.getScenario(ScenarioID), ScenarioManager.EmptyScenario):
            return None
            pass

        ScenarioDesc = ScenarioManager.getScenario(ScenarioID)

        if ScenarioDesc is None:
            return None
            pass

        isZoom = ScenarioDesc.ZoomName is not None

        if isZoom is True:
            GroupName = ScenarioDesc.ZoomName
        else:
            GroupName = SceneManager.getSceneMainGroupName(ScenarioDesc.SceneName)
            pass

        return GroupName
