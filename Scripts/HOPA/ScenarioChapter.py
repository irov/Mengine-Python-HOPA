from Foundation.Initializer import Initializer
from Foundation.Notificator import Notificator
from Notification import Notification

class ScenarioChapter(Initializer):
    def __init__(self):
        super(ScenarioChapter, self).__init__()

        self.scenarios = {}
        self.Options = {}

        self.paragraphComplete = []

        self.skipedInjections = []

        self.onParagraphRunObserver = None
        pass

    def addScenario(self, ScenarioID, Runner):
        if Runner is None:
            Trace.log("Manager", 0, "ScenarioChapter.addScenario %s Runner is None" % (ScenarioID))

            return False
            pass

        self.scenarios[ScenarioID] = Runner

        return True
        pass

    def getScenario(self, ScenarioID):
        if ScenarioID not in self.scenarios:
            return None
            pass

        Runner = self.scenarios[ScenarioID]

        return Runner
        pass

    def addOption(self, name, value):
        self.Options[name] = value
        pass

    def setOptions(self, options):
        self.Options = options
        pass

    def getOptions(self):
        return self.Options
        pass

    def visitScenario(self, cb):
        for scenario in self.scenarios.itervalues():
            cb(scenario)
            pass
        pass

    def _onInitialize(self):
        super(ScenarioChapter, self)._onInitialize()

        self.onParagraphRunObserver = Notification.addObserver(Notificator.onParagraphRun, self.__onParagraphRun)
        pass

    def __onParagraphRun(self, ParagraphID):
        self.completeParagraph(ParagraphID)

        return False
        pass

    def _onFinalize(self):
        super(ScenarioChapter, self)._onFinalize()

        Notification.removeObserver(self.onParagraphRunObserver)

        for scenario in self.scenarios.itervalues():
            scenario.onFinalize()
            pass

        self.paragraphComplete = []
        self.scenarios = {}
        pass

    def _onInitializeFailed(self, msg):
        Trace.log("Manager", 0, "ScenarioChapter initialize failed: %s" % (msg))
        pass

    def _onFinalizeFailed(self, msg):
        Trace.log("Manager", 0, "ScenarioChapter finalize failed: %s" % (msg))
        pass

    def run(self):
        if _DEVELOPMENT is True:
            Mengine.watchdog("ScenarioChapter init")
            pass

        for scenario in self.scenarios.itervalues():
            scenario.onInitialize()
            pass

        if _DEVELOPMENT is True:
            print("ScenarioChapter init %f" % (Mengine.watchdog("ScenarioChapter init")))
            pass

        if _DEVELOPMENT is True:
            Mengine.watchdog("ScenarioChapter generate")
            pass

        for scenario in self.scenarios.itervalues():
            if scenario.generateScenario(self) is False:
                Trace.log("Manager", 0, "ScenarioChapter.run scenario invalid generate")

                return False
                pass
            pass

        if _DEVELOPMENT is True:
            print("ScenarioChapter generate %f" % (Mengine.watchdog("ScenarioChapter generate")))
            pass

        if _DEVELOPMENT is True:
            Mengine.watchdog("ScenarioChapter run")

        for scenario in self.scenarios.itervalues():
            if scenario.run() is False:
                Trace.log("Manager", 0, "ScenarioChapter.run scenario invalid run")
                return False
                pass
            pass

        if _DEVELOPMENT is True:
            print("ScenarioChapter run %f" % (Mengine.watchdog("ScenarioChapter run")))
            pass

        return True
        pass

    def stop(self):
        for scenario in self.scenarios.itervalues():
            scenario.skip()
            scenario.stop()
            pass
        pass

    def skip(self):
        for scenario in self.scenarios.itervalues():
            scenario.skip()
            pass
        pass

    def skipScenario(self, scenarioID):
        ScenarioRunner = self.scenarios[scenarioID]
        ScenarioRunner.skip()
        pass

    def save(self):
        save_scenarios = []

        for name, scenario in self.scenarios.iteritems():
            save_scenario = scenario.save()
            save_scenario_data = (name, save_scenario)
            save_scenarios.append(save_scenario_data)
            pass

        save_data = (save_scenarios, self.paragraphComplete, self.skipedInjections)

        return save_data
        pass

    def load(self, load_chapter):
        if load_chapter is None:
            Trace.log("Manager", 0, "ScenarioChapter.load load_chapter is None")
            return False
            pass

        load_scenarios, paragraphComplete, self.skipedInjections = load_chapter

        for load_data in load_scenarios:
            name, load_macro = load_data
            if name not in self.scenarios.keys():
                from HOPA.ChapterManager import ChapterManager
                if name in self.skipedInjections:
                    continue
                scenario = ChapterManager.chapterAddInjection(self, name)
                pass
            else:
                scenario = self.scenarios[name]
                pass

            if scenario is None:
                return False
                pass

            scenario.load(load_macro)
            pass

        self.paragraphComplete = paragraphComplete

        return True
        pass

    def skipInjection(self, Injection):
        self.skipedInjections.append(Injection)
        pass

    def completeParagraph(self, paragraphID):
        self.paragraphComplete.append(paragraphID)
        Notification.notify(Notificator.onParagraphComplete, paragraphID)
        pass

    def isParagraphComplete(self, paragraphID):
        return paragraphID in self.paragraphComplete
        pass

    def findSceneScenarios(self, SceneName):
        SceneScenarios = []
        for Scenario in self.scenarios.itervalues():
            if Scenario.SceneName == SceneName:
                SceneScenarios.append(Scenario)
                pass
            pass

        return SceneScenarios
        pass

    def findSceneGroupScenarios(self, SceneName, GroupName):
        SceneScenarios = []
        for Scenario in self.scenarios.itervalues():
            if Scenario.SceneName == SceneName and Scenario.GroupName == GroupName:
                SceneScenarios.append(Scenario)
                pass
            pass

        return SceneScenarios
        pass

    def filterAllSceneScenario(self, SceneName, CommandTypeFilter):
        SceneScenarios = self.findSceneScenarios(SceneName)
        SceneCommands = []

        for Scenario in SceneScenarios:
            MacroCommands = Scenario.getMacroCommands()
            # print 'filterAllSceneScenario MacroCommands len =', len(MacroCommands)
            for MacroCommandHandle in MacroCommands.itervalues():
                if MacroCommandHandle.CommandType not in CommandTypeFilter:
                    continue
                    pass

                SceneCommands.append(MacroCommandHandle)
                pass
            pass

        return SceneCommands
        pass

    def findAllSceneScenarioParagraphs(self, SceneName):
        SceneScenarioRunners = self.findSceneScenarios(SceneName)
        SceneParagraphs = []

        for ScenarioRunner in SceneScenarioRunners:
            Scenario = ScenarioRunner.Scenario
            SceneParagraphs += Scenario.getParagraphs()

        return SceneParagraphs

    def filterSceneScenario(self, SceneName, CommandTypeFilter):
        SceneCommands = self.filterAllSceneScenario(SceneName, CommandTypeFilter)

        return SceneCommands
        pass

    def filterSceneScenarioRun(self, SceneName, CommandTypeFilter):
        SceneCommands = self.filterAllSceneScenario(SceneName, CommandTypeFilter)

        SceneCommandsRun = []

        for SceneCommand in SceneCommands:
            if SceneCommand.Run is False:
                continue
                pass

            SceneCommandsRun.append(SceneCommand)
            pass

        return SceneCommandsRun
        pass
    pass