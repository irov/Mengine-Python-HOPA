from Foundation.DatabaseManager import DatabaseManager
from Foundation.GroupManager import GroupManager
from Foundation.SceneManager import SceneManager
from HOPA.QuestManager import QuestManager
from HOPA.TransitionManager import TransitionManager
from HOPA.ZoomManager import ZoomManager

class CruiseControlManager(object):
    s_cruiseTypes = {}
    s_questsType = {}
    s_policy = {}
    s_validateCruiseTypes = []
    s_blackList = []
    s_sceneExceptions = {}
    s_cruiseDelays = {}

    s_actions = {}
    s_mask = None

    class Cruise(object):
        def __init__(self, cruiseActionType, cruiseGlobal, cruisePriority):
            self.cruiseActionType = cruiseActionType
            self.cruiseGlobal = cruiseGlobal
            self.cruisePriority = cruisePriority
            pass

        def isGlobal(self):
            return self.cruiseGlobal
            pass

        def isCruise(self):
            return self.validCruise
            pass

        def getPriority(self):
            return self.cruisePriority
            pass
        pass

    @staticmethod
    def onFinalize():
        CruiseControlManager.s_cruiseTypes = {}
        CruiseControlManager.s_actions = {}
        CruiseControlManager.s_sceneExceptions = {}
        CruiseControlManager.s_questsType = {}
        CruiseControlManager.s_blackList = []
        CruiseControlManager.s_mask = None
        CruiseControlManager.s_cruiseDelays = {}
        pass

    @staticmethod
    def loadParams(module, param):
        if param == "CruiseControl":
            CruiseControlManager.loadCruiseActions(module, "CruiseControl")
            pass
        if param == "ValidateCruiseActions":
            CruiseControlManager.loadValidateCruiseActions(module, "ValidateCruiseActions")
            pass
        if param == "CruiseActionsDelays":
            CruiseControlManager.loadCruiseActionsDelays(module, "CruiseActionsDelays")

        return True
        pass

    @staticmethod
    def loadCruiseActionsDelays(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            CruiseActionName = record.get("CruiseActionName")
            ClickDelay = record.get("ClickDelay")
            MoveDelay = record.get("MoveDelay")
            CruiseControlManager.s_cruiseDelays[CruiseActionName] = {"ClickDelay": ClickDelay, "MoveDelay": MoveDelay}

    @staticmethod
    def loadCruiseActions(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            QuestType = record.get("QuestType")
            CruiseAction = record.get("CruiseAction")
            Global = bool(record.get("Global"))
            Priority = record.get("Priority")

            CruiseControlManager.s_cruiseTypes[QuestType] = CruiseControlManager.Cruise(CruiseAction, Global, Priority)
            CruiseControlManager.s_questsType[QuestType] = CruiseAction
            pass
        pass

    @staticmethod
    def loadCruiseActionsPolicy(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)
        for record in records:
            Action = record.get("Action")
            Policy = record.get("Policy")

            CruiseControlManager.s_policy[Action] = Policy
            pass
        pass

    @staticmethod
    def getCruiseActionPolicy(cruiseActionName):
        if cruiseActionName not in CruiseControlManager.s_policy.keys():
            Trace.log("Manager", 0, "CruiseControlManager getCruiseActionPolicy: %s not in list" % (cruiseActionName))
            return None

        return CruiseControlManager.s_policy[cruiseActionName]
        pass

    @staticmethod
    def loadValidateCruiseActions(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            CruiseActionName = record.get("CruiseActionName")
            isCruise = bool(record.get("isCruise"))

            if isCruise is True:
                CruiseControlManager.s_validateCruiseTypes.append(CruiseActionName)
                pass
            pass
        pass

    @staticmethod
    def loadSceneExceptions(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            ExceptionID = record.get("ExceptionID")
            MindID = record.get("MindID")

            CruiseControlManager.s_sceneExceptions[ExceptionID] = MindID
            pass
        pass

    @staticmethod
    def loadBlackList(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            ObjectName = record.get("ObjectName")
            GroupName = record.get("GroupName")

            Object = GroupManager.getObject(GroupName, ObjectName)

            CruiseControlManager.s_blackList.append(Object)
            pass
        pass

    @staticmethod
    def inBlackList(object):
        return object in CruiseControlManager.s_blackList
        pass

    @staticmethod
    def hasSceneException(exceptionID):
        return exceptionID in CruiseControlManager.s_sceneExceptions
        pass

    @staticmethod
    def getSceneExceptionMindID(exceptionID):
        return CruiseControlManager.s_sceneExceptions[exceptionID]
        pass

    @staticmethod
    def importCruiseActions(module, names):
        for name in names:
            CruiseControlManager.importCruiseAction(module, name)
            pass
        pass

    @staticmethod
    def importCruiseAction(module, name):
        Name = "%s" % (name)
        FromName = module
        ModuleName = "%s.%s" % (FromName, Name)
        Module = __import__(ModuleName, fromlist=[FromName])
        Type = getattr(Module, Name)
        CruiseControlManager.addCruiseAction(name, Type)
        pass

    @staticmethod
    def setMask(mask):
        CruiseControlManager.s_mask = mask
        pass

    @staticmethod
    def clearMask():
        CruiseControlManager.s_mask = None
        pass

    @staticmethod
    def getCruiseClickDelay(cruiseType, default=0):
        cruise_delays = CruiseControlManager.s_cruiseDelays.get(cruiseType, {})
        return cruise_delays.get("ClickDelay", default)

    @staticmethod
    def getCruiseMoveDelay(cruiseType, default=0):
        cruise_delays = CruiseControlManager.s_cruiseDelays.get(cruiseType, {})
        return cruise_delays.get("MoveDelay", default)

    @staticmethod
    def getCruisePriority(cruiseType):
        cruise = CruiseControlManager.s_cruiseTypes[cruiseType]

        return cruise.getPriority()
        pass

    @staticmethod
    def addCruiseAction(actionType, action):
        CruiseControlManager.s_actions[actionType] = action
        pass

    @staticmethod
    def getCruiseActionType(questType):
        return CruiseControlManager.s_questsType[questType]
        pass

    @staticmethod
    def isValidateCruise(cruiseActionType):
        return cruiseActionType in CruiseControlManager.s_validateCruiseTypes
        pass

    @staticmethod
    def getCruiseAction(actionType):
        action = CruiseControlManager.s_actions[actionType]

        return action
        pass

    @staticmethod
    def createCruiseAction(cruiseActionType, quest, **params):
        cruiseAction = CruiseControlManager.getCruiseAction(cruiseActionType)

        if cruiseAction is None:
            return None
            pass

        cruiseAction = cruiseAction()
        cruiseAction.setType(cruiseActionType)
        cruiseAction.onParams(params)
        cruiseAction.setQuest(quest)
        cruiseAction.onInitialize()

        return cruiseAction
        pass

    @staticmethod
    def findSceneCruise(sceneName, groupName, checkActive):
        if sceneName == "CutScene":
            cruiseAction = CruiseControlManager.createCruiseAction("CruiseActionCutScene", None)
            return cruiseAction

        localQuestsCache = QuestManager.getLocalQuests(sceneName, groupName)
        cruiseAction = CruiseControlManager.findCruise(localQuestsCache, checkActive)

        if cruiseAction is None:
            questSceneCache = QuestManager.getSceneQuests(sceneName, groupName)
            cruiseAction = CruiseControlManager.findCruise(questSceneCache, checkActive)
            pass

        return cruiseAction
        pass

    @staticmethod
    def findGlobalCruise():
        questGlobalCache = QuestManager.getGlobalQuests()
        cruiseAction = CruiseControlManager.findCruise(questGlobalCache, True)
        return cruiseAction
        pass

    @staticmethod
    def findCruise(questCache, checkActive):
        """
        receive cruise actions list
        choose most relevant one
        """
        cruiseActionList = CruiseControlManager.__createCruiseActionList(questCache, checkActive)
        if cruiseActionList.__len__() == 0:
            return  # action not found

        for cruiseAction in cruiseActionList:
            if cruiseAction.getType() == "CruiseActionDummy":
                continue

            return cruiseAction  # return first not dummy action

        # default return
        return cruiseActionList[0]

    @staticmethod
    def __createCruiseActionList(questCache, checkActive):
        if questCache is None:
            return []

        OutCruiseActions = []  # cruise list to return

        for quest in questCache[:]:
            if quest.isComplete() is True:
                questCache.remove(quest)
                continue

            if checkActive is True:
                if quest.active is False:
                    continue

            if quest.questType not in CruiseControlManager.s_cruiseTypes:
                continue

            if quest.questType == "EnterZoom":
                ZoomGroupName = quest.params.get("GroupName")
                zoom = ZoomManager.getZoom(ZoomGroupName)
                if zoom.hasObject() is False:
                    continue

                ZoomObject = ZoomManager.getZoomObject(ZoomGroupName)
                Params = dict(Zoom=ZoomObject)

                cruiseAction = CruiseControlManager.createCruiseAction("CruiseActionZoom", quest, **Params)

            elif quest.questType == "EnterScene":
                CruiseSceneName = quest.params.get("SceneName")
                currentSceneName = SceneManager.getCurrentSceneName()
                TransitionObject = TransitionManager.findTransitionObjectToScene(currentSceneName, CruiseSceneName)

                if TransitionObject is not None:
                    Params = dict(Transition=TransitionObject)
                    cruiseAction = CruiseControlManager.createCruiseAction("CruiseActionTransition", quest, **Params)
                else:
                    TransitionBack = TransitionManager.findTransitionBackToScene(currentSceneName, CruiseSceneName)
                    if TransitionBack is not None:
                        Params = dict(Transition=TransitionBack)
                        cruiseAction = CruiseControlManager.createCruiseAction("CruiseActionTransitionBack", quest, **Params)
                    else:
                        continue

            else:
                cruiseActionType = CruiseControlManager.getCruiseActionType(quest.questType)
                cruiseAction = CruiseControlManager.createCruiseAction(cruiseActionType, quest, **quest.params)

            if cruiseAction is None:
                continue

            if cruiseAction.onCheck() is False:
                continue

            if cruiseAction.getType() == "CruiseActionDummy":  # hack to flush looping dummy action
                if quest.questType == "Play":
                    object_ = quest.params.get("Object")
                    if object_.getLoop():
                        # "CruiseControlManager quest Dummy is play loop {}, continue", object_.getName()
                        continue

            OutCruiseActions.append(cruiseAction)

        return OutCruiseActions