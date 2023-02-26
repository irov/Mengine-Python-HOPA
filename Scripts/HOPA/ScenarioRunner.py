from Foundation.Initializer import Initializer
from Notification import Notification

class ScenarioRunner(Initializer):
    class MacroCommandHandler(object):
        def __init__(self, CommandType):
            self.CommandType = CommandType
            self.Run = False
            pass

        def setRun(self, value):
            self.Run = value
            pass
        pass

    def __init__(self, Name, SceneName, GroupName, isZoom, Scenario, isPlusScene):
        super(ScenarioRunner, self).__init__()

        self.macroRun = []
        self.macroEnd = []

        self.tcs = []

        self.Scenario = Scenario

        self.macroCommands = {}

        self.Name = Name

        self.SceneName = SceneName
        self.GroupName = GroupName

        self.isZoom = isZoom
        self.isPlusScene = isPlusScene
        pass

    def _onInitialize(self):
        super(ScenarioRunner, self)._onInitialize()
        pass

    def _onFinalize(self):
        super(ScenarioRunner, self)._onFinalize()

        self.stop()

        self.tcs = []

        self.macroRun = []
        self.macroEnd = []

        self.macroCommands = {}

        self.Scenario = None
        pass

    def getScenario(self):
        return self.Scenario
        pass

    def getName(self):
        return self.Name
        pass

    def getSceneName(self):
        return self.SceneName
        pass

    def getGroupName(self):
        return self.GroupName
        pass

    def runMacro(self, Index):
        self.macroRun.append(Index)
        pass

    def isMacroRun(self, Index):
        return Index in self.macroRun
        pass

    def endMacro(self, Index):
        self.macroEnd.append(Index)
        pass

    def isMacroEnd(self, Index):
        return Index in self.macroEnd
        pass

    def runCommand(self, ID):
        handler = self.macroCommands[ID]
        handler.setRun(True)

        Notification.notify(Notificator.onMacroCommandRun, ID, handler.CommandType, self.SceneName, self.GroupName)
        pass

    def endCommand(self, ID):
        if ID in self.macroCommands:
            handler = self.macroCommands.pop(ID)
            Notification.notify(Notificator.onMacroCommandEnd, ID, handler.CommandType, self.SceneName, self.GroupName)
            pass
        pass

    def generateScenario(self, ScenarioChapter):
        self.tcs = self.Scenario.onGenerator(self, ScenarioChapter)
        pass

    def createMacroCommand(self, Command):
        CommandType = Command.getCommandType()
        handler = ScenarioRunner.MacroCommandHandler(CommandType)

        ID = Command.getCommandId()
        self.macroCommands[ID] = handler

        return ID
        pass

    def getMacroCommands(self):
        return self.macroCommands
        pass

    def getMacroCommand(self, ID):
        return self.macroCommands.get(ID, None)
        pass

    def run(self):
        # Mengine.watchdog("Scenario run")
        for tc in self.tcs:
            try:
                if tc.run() is False:
                    Trace.log("Manager", 0, "ScenarioRunner.run SceneName '%s' GroupName '%s' invalid run task chain" % (self.SceneName, self.GroupName))

                    return False
                    pass
            except Exception as ex:
                traceback.print_exc()

                Trace.log("Manager", 0, "ScenarioRunner.run: SceneName '%s' GroupName '%s' except run task chain: %s" % (self.SceneName, self.GroupName, ex))

                return False
                pass
            pass

        return True
        pass

    def stop(self):
        for tc in self.tcs:
            tc.cancel()
            pass
        pass

    def skip(self):
        for tc in self.tcs:
            tc.skip()
            pass
        pass

    def save(self):
        save_data = (self.macroEnd, True)

        return save_data
        pass

    def load(self, load_data):
        macroEnd, Valid = load_data

        self.macroEnd = macroEnd
        pass
    pass