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

    def getCommandType(self):
        return self.CommandType

    def setIndex(self, Index):
        self.Index = Index

    def getIndex(self):
        return self.Index

    def setCommandId(self, ID):
        self.ID = ID

    def getCommandId(self):
        return self.ID

    def setGroupName(self, GroupName):
        self.GroupName = GroupName

    def getGroupName(self):
        return self.GroupName

    def setSceneName(self, ScenName):
        self.SceneName = ScenName

    def setScenarioRunner(self, ScenarioRunner):
        self.ScenarioRunner = ScenarioRunner

    def setScenarioChapter(self, ScenarioChapter):
        self.ScenarioChapter = ScenarioChapter

    def setScenarioCommands(self, ScenarioCommands):
        self.ScenarioCommands = ScenarioCommands

    def getScenarioCommands(self):
        return self.ScenarioCommands

    def setScenarioQuests(self, ScenarioQuests):
        self.ScenarioQuests = ScenarioQuests

    def setRepeatScenario(self, Value):
        self.RepeatScenario = Value

    def isRepeatScenario(self):
        return self.RepeatScenario

    def onParams(self, params):
        if len(params) == 0:
            self.initializeFailed("MacroCommand '%s' Group '%s' (index %s) ERROR: params is empty" %
                                  (self.CommandType, self.GroupName, self.Index))

        try:
            self._onParams(params)
        except Exception as ex:
            traceback.print_exc()

            self.initializeFailed("MacroCommand '%s' Group '%s' (index %s) params %s ERROR: %s" %(self.CommandType, self.GroupName, self.Index, params, ex))
            pass

    def _onParams(self, params):
        self.GroupName = params["GroupName"]
        self.SceneName = params["SceneName"]

    def onValues(self, values):
        try:
            self._onValues(values)
        except Exception as ex:
            traceback.print_exc()

            Trace.log("Command", 0, "MacroCommand '%s' Group '%s' index %d values %s ERROR: '%s'" % (self.CommandType, self.GroupName, self.Index, values, ex))
            pass

    def _onValues(self, values):
        pass

    def addQuest(self, source, questType, **Params):
        if _DEVELOPMENT is True and "hint" in Mengine.getOptionValues("debug"):
            Params["FromMacroCommand"] = self.__class__.__name__
            Params["__INDEX"] = self.Index
        Quest = QuestManager.createScenarioQuest(questType, self.isTechnical, **Params)

        if Quest is None:
            Trace.log("Command", 0, "MacroCommand '%s' [%s] createScenarioQuest questType %s is None" %
                                    (self.CommandType, self.GroupName, questType))
            return None

        QuestWith = QuestManager.runQuest(source, Quest)

        self.ScenarioQuests.append(Quest)

        return QuestWith

    def onGenerate(self, source):
        self._onGenerate(source)

    def _onGenerate(self, source):
        pass

    def _onInitializeFailed(self, msg):
        description = "MacroCommand '%s' initialize failed at Group '%s' (index %d) failed with error: %s" % (
            self.CommandType, self.GroupName, self.Index, msg)

        Trace.log("Command", 0, description)

    def _onFinalizeFailed(self, msg):
        description = "MacroCommand '%s' finalize failed at Group '%s' (index %d) failed with error: %s" % (
            self.CommandType, self.GroupName, self.Index, msg)

        Trace.log("Command", 0, description)

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
                    Trace.log("Command", 0, "MacroCommand '%s' findObject: Item '%s' in ItemManager has group '%s', not '%s' as expected" %
                                            (self.CommandType, Object.name, ItemGroupName, self.GroupName))
                    return None, None

            return FinderType, Object

        if GroupManager.hasObject(self.GroupName, name) is True:
            Object = GroupManager.getObject(self.GroupName, name)
            return "GroupManager", Object

        Zoom = ZoomManager.getZoom(self.GroupName)
        if Zoom is not None:
            OverFrameGroupName = Zoom.getOverFrameGroupName()
            if OverFrameGroupName is not None and GroupManager.hasObject(OverFrameGroupName, name) is True:
                Object = GroupManager.getObject(OverFrameGroupName, name)
                return "GroupManager", Object

        self.initializeFailed("%s findObject: not found object '%s' at Group %s" % (self.CommandType, name, self.GroupName))
        return None

    def filterObject(self, name, filters):
        FinderType, Object = self.findObject(self.ObjectName)

        ObjectType = Object.getType()
        if ObjectType not in filters:
            return False
            pass

        return True
