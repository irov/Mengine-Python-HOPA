from Foundation.DatabaseManager import DatabaseManager

from HOPA.Macro.MacroCommandFactory import MacroCommandFactory

class MacroManager(object):
    s_macroTypes = {}
    s_commandsQuestFilter = {}

    s_macroces = {}
    s_finders = {}

    s_enumerate = 0

    @staticmethod
    def onFinalize():
        for macro in MacroManager.s_macroces.itervalues():
            macro.onFinalize()
            pass

        MacroManager.s_macroces = {}
        MacroManager.s_commandsQuestFilter = {}

        MacroManager.s_enumerate = 0
        pass

    @staticmethod
    def addFinder(name, finder):
        MacroManager.s_finders[name] = finder
        pass

    @staticmethod
    def loadParams(module, param):
        if param == "MacroCommands":
            if MacroManager.loadMacroCommands(module, "MacroCommands") is False:
                return False
                pass
            pass
        if param == "CommandsQuestFilter":
            if MacroManager.loadCommandsQuestFilter(module, "SceneSlots") is False:
                return False
                pass
            pass

        return True
        pass

    @staticmethod
    def loadMacroCommands(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            CommandName = record.get("CommandName")
            Module = record.get("Module")
            Type = record.get("Type")

            if MacroManager.importMacroCommand(Module, CommandName, Type) is False:
                return False
                pass
            pass

        return True
        pass

    @staticmethod
    def loadCommandsQuestFilter(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        if records is None:
            return False
            pass

        for record in records:
            CommandType = record.get("CommandType")
            FilterObjectTypes = record.get("FilterObjectTypes")

            MacroManager.s_commandsQuestFilter[CommandType] = FilterObjectTypes
            pass

        return True
        pass

    @staticmethod
    def hasCommandsQuestFilter():
        if len(MacroManager.s_commandsQuestFilter) > 0:
            return True
            pass

        return False
        pass

    @staticmethod
    def getCommandsQuestFilter():
        return MacroManager.s_commandsQuestFilter
        pass

    @staticmethod
    def importMacroCommand(module, commandName, commandType):
        try:
            FromName = module
            ModuleName = "%s.%s" % (FromName, commandType)
            Module = __import__(ModuleName, fromlist=[FromName])
            Type = getattr(Module, commandType)
        except ImportError as ex:
            Trace.log("Manager", 0, "invalid import macro command %s command name %s type %s except error: %s", module, commandName, commandType, ex)

            return False
            pass

        MacroCommandFactory.addCommandType(commandName, Type)

        return True
        pass

    @staticmethod
    def removeFinder(name):
        del MacroManager.s_finders[name]
        pass

    @staticmethod
    def findObject(name, filter=None):
        for finderName, finder in MacroManager.s_finders.iteritems():
            find_object = finder(name)

            if find_object is None:
                continue
                pass

            if filter is not None:
                find_object_type = find_object.getType()

                if find_object_type not in filter:
                    continue
                    pass
                pass

            return (finderName, find_object)
            pass

        return (None, None)
        pass

    @staticmethod
    def loadMacroses(module, param):
        mcs = {}
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            Name = record.get("Name")
            GroupName = record.get("GroupName")
            ZoomName = record.get("ZoomName")

            mc = MacroManager.loadMacro(Name, GroupName, ZoomName)
            mcs[Name] = mc
            pass

        return mcs
        pass

    @staticmethod
    def loadMacro(paramName, sceneName, zoomName=None):
        if paramName in MacroManager.s_macroces:
            Trace.log("Manager", 0, "MacroManager already load macro %s:%s:%s" % (paramName, sceneName, zoomName))
            return None
            pass

        mc = Macro(paramName, sceneName, zoomName)

        mc.onInitialize()

        mc.parse()

        MacroManager.s_macroces[paramName] = mc

        return mc
        pass

    @staticmethod
    def removeMacro(macro):
        macro.onFinalize()

        del MacroManager.s_macroces[macro.ParamName]
        pass

    @staticmethod
    def findSceneMacroces(sceneName):
        SceneMacroces = []
        for macro in MacroManager.s_macroces.itervalues():
            if macro.SceneName == sceneName:
                SceneMacroces.append(macro)
            pass
        return SceneMacroces

    @staticmethod
    def filterAllSceneMacro(SceneName, MacroTypeFilter):
        SceneMacroces = MacroManager.findSceneMacroces(SceneName)
        SceneCommands = []

        for macro in SceneMacroces:
            for macroBaseSceneCache in macro.commands.itervalues():
                MacroType = macroBaseSceneCache.CommandType
                if MacroType not in MacroTypeFilter:
                    continue
                    pass

                SceneCommands.append(macroBaseSceneCache)
                pass
            pass
            pass

        return SceneCommands
        pass

    @staticmethod
    def filterSceneMacro(SceneName, MacroTypeFilter):
        SceneCommands = MacroManager.filterAllSceneMacro(SceneName, MacroTypeFilter)

        return SceneCommands
        pass

    @staticmethod
    def filterSceneMacroRun(SceneName, MacroTypeFilter):
        SceneCommands = MacroManager.filterAllSceneMacro(SceneName, MacroTypeFilter)

        RunSceneMacroces = []

        for macroBaseSceneCache in SceneCommands:
            if macroBaseSceneCache.Run is False:
                continue
                pass

            RunSceneMacroces.append(macroBaseSceneCache)
            pass

        return RunSceneMacroces
        pass
    pass