from Foundation.GroupManager import GroupManager
from Foundation.Initializer import Initializer
from HOPA.MacroManager import MacroManager
from HOPA.QuestManager import QuestManager
from HOPA.ZoomManager import ZoomManager


class MacroCommand(Initializer):
    Immediately = False

    def __init__(self):
        super(MacroCommand, self).__init__()

        self.CommandType = None

        self.ScenarioRunner = None
        self.ScenarioChapter = None
        self.ScenarioCommands = None
        self.ScenarioQuests = None

        self.Index = None
        self.ID = None

        self.GroupName = None
        self.SceneName = None

        self.RepeatScenario = False
        self.isTechnical = False
        pass

    def setCommandType(self, CommandType):
        self.CommandType = CommandType
        pass

    def getCommandType(self):
        return self.CommandType
        pass

    def setIndex(self, Index):
        self.Index = Index
        pass

    def getIndex(self):
        return self.Index
        pass

    def setCommandId(self, ID):
        self.ID = ID
        pass

    def getCommandId(self):
        return self.ID
        pass

    def setGroupName(self, GroupName):
        self.GroupName = GroupName
        pass

    def getGroupName(self):
        return self.GroupName
        pass

    def setSceneName(self, ScenName):
        self.SceneName = ScenName
        pass

    def setScenarioRunner(self, ScenarioRunner):
        self.ScenarioRunner = ScenarioRunner
        pass

    def setScenarioChapter(self, ScenarioChapter):
        self.ScenarioChapter = ScenarioChapter
        pass

    def setScenarioCommands(self, ScenarioCommands):
        self.ScenarioCommands = ScenarioCommands
        pass

    def getScenarioCommands(self):
        return self.ScenarioCommands
        pass

    def setScenarioQuests(self, ScenarioQuests):
        self.ScenarioQuests = ScenarioQuests
        pass

    def setRepeatScenario(self, Value):
        self.RepeatScenario = Value
        pass

    def isRepeatScenario(self):
        return self.RepeatScenario
        pass

    def onParams(self, params):
        if len(params) == 0:
            self.initializeFailed("Macro %s not add any param, group %s:%s" % (self.CommandType, self.GroupName, self.Index))
            pass

        try:
            self._onParams(params)
        except Exception as ex:
            traceback.print_exc()

            self.initializeFailed("Macro %s group %s:%s except params: %s" % (self.CommandType, self.GroupName, self.Index, ex))

    def _onParams(self, params):
        self.GroupName = params["GroupName"]
        self.SceneName = params["SceneName"]
        pass

    def onValues(self, values):
        try:
            self._onValues(values)
        except Exception as ex:
            traceback.print_exc()

            Trace.log("Command", 0, "MacroCommand.onValues: command %s group %s index %d values %s except: '%s'" % (
                self.CommandType, self.GroupName, self.Index, values, ex))

    def _onValues(self, values):
        pass

    def addQuest(self, source, questType, **Params):
        if _DEVELOPMENT is True and "hint" in Mengine.getOptionValues("debug"):
            Params["FromMacroCommand"] = self.__class__.__name__
            Params["__INDEX"] = self.Index
        Quest = QuestManager.createScenarioQuest(questType, self.isTechnical, **Params)

        if Quest is None:
            Trace.log("Command", 0, "MacroCommand.addQuest: createScenarioQuest questType %s is None" % (questType))
            return None
            pass

        QuestWith = QuestManager.runQuest(source, Quest)

        self.ScenarioQuests.append(Quest)

        return QuestWith
        pass

    def onGenerate(self, source):
        self._onGenerate(source)

    def _onGenerate(self, source):
        pass

    def _onInitializeFailed(self, msg):
        Trace.log("Command", 0, "MacroCommand initialize failed %s macro %s:%d failed %s" % (
            self.CommandType, self.GroupName, self.Index, msg))
        pass

    def _onFinalizeFailed(self, msg):
        Trace.log("Command", 0, "MacroCommand finalize failed %s macro %s:%d failed %s" % (
            self.CommandType, self.GroupName, self.Index, msg))
        pass

    def hasObject(self, name, filter=None):
        FinderType, Object = MacroManager.findObject(name, filter)

        if Object is not None:
            return True
            pass

        if GroupManager.hasObject(self.GroupName, name) is True:
            return True
            pass

        if ZoomManager.hasZoom(self.GroupName) is True:
            Zoom = ZoomManager.getZoom(self.GroupName)
            if Zoom is not None:
                OverFrameGroupName = Zoom.getOverFrameGroupName()

                if OverFrameGroupName is not None and GroupManager.hasObject(OverFrameGroupName, name) is True:
                    return True

        return False

    def findObject(self, name, filter=None):
        FinderType, Object = MacroManager.findObject(name, filter)

        if Object is not None:
            if Object.getType() is "ObjectItem":
                ItemGroupName = Object.getGroupName()
                if self.GroupName != ItemGroupName:
                    Trace.log("Command", 0, "MacroCommand.findObject: Item %s in ItemManager has any group - %s, not %s!!!!!!" % (
                              Object.name, ItemGroupName, self.GroupName))
                    return None, None

            return FinderType, Object
            pass

        if GroupManager.hasObject(self.GroupName, name) is True:
            Object = GroupManager.getObject(self.GroupName, name)
            return "GroupManager", Object
            pass

        Zoom = ZoomManager.getZoom(self.GroupName)
        if Zoom is not None:
            OverFrameGroupName = Zoom.getOverFrameGroupName()
            if OverFrameGroupName is not None and GroupManager.hasObject(OverFrameGroupName, name) is True:
                Object = GroupManager.getObject(OverFrameGroupName, name)
                return "GroupManager", Object
                pass

        self.initializeFailed("%s findObject: %s not found %s" % (self.CommandType, self.GroupName, name))
        return None
        pass

    def filterObject(self, name, filters):
        FinderType, Object = self.findObject(self.ObjectName)

        ObjectType = Object.getType()
        if ObjectType not in filters:
            return False
            pass

        return True
