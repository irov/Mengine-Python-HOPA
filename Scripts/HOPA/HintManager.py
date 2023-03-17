from Foundation.DatabaseManager import DatabaseManager
from Foundation.GroupManager import GroupManager
from Foundation.Notificator import Notificator
from Foundation.SceneManager import SceneManager
from HOPA.QuestManager import QuestManager
from HOPA.TransitionManager import TransitionManager
from HOPA.ZoomManager import ZoomManager
from Notification import Notification


class HintManager(object):
    s_hintTypes = {}
    s_questsType = {}
    s_policy = {}
    s_validateHintTypes = []
    s_blackList = []
    s_sceneExceptions = {}

    s_actions = {}
    s_mask = None

    class Hint(object):
        def __init__(self, hintActionType, hintGlobal, hintPriority):
            self.hintActionType = hintActionType
            self.hintGlobal = hintGlobal
            self.hintPriority = hintPriority
            self.validHint = True

        def isGlobal(self):
            return self.hintGlobal

        def isHint(self):
            return self.validHint

        def getPriority(self):
            return self.hintPriority

    @staticmethod
    def onFinalize():
        HintManager.s_hintTypes = {}
        HintManager.s_actions = {}
        HintManager.s_sceneExceptions = {}
        HintManager.s_questsType = {}
        HintManager.s_blackList = []
        HintManager.s_mask = None

    @staticmethod
    def loadParams(module, param):
        if param == "HintActions":
            HintManager.loadHintActions(module, "HintActions")
        if param == "ValidateHintActions":
            HintManager.loadValidateHintActions(module, "ValidateHintActions")
        if param == "HintMinds":
            HintManager.loadSceneExceptions(module, "HintMinds")
        if param == "HintBlackList":
            HintManager.loadBlackList(module, "HintBlackList")
        return True

    @staticmethod
    def loadHintActions(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            QuestType = record.get("QuestType")
            HintAction = record.get("HintAction")
            Global = bool(record.get("Global"))
            Priority = record.get("Priority")

            HintManager.s_hintTypes[QuestType] = HintManager.Hint(HintAction, Global, Priority)
            HintManager.s_questsType[QuestType] = HintAction

        HintManager.s_hintTypes["Dummy"] = HintManager.Hint("HintActionDummy", 0, 0)
        HintManager.s_questsType["Dummy"] = "HintActionDummy"

    @staticmethod
    def loadHintActionsPolicy(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)
        for record in records:
            Action = record.get("Action")
            Policy = record.get("Policy")
            HintManager.s_policy[Action] = Policy

    @staticmethod
    def getHintActionPolicy(hintActionName):
        if hintActionName not in HintManager.s_policy.keys():
            Trace.log("Manager", 0, "HintManager getHintActionPolicy: %s not in list" % hintActionName)
            return None
        return HintManager.s_policy[hintActionName]

    @staticmethod
    def currentHintEnd():
        Notification.notify(Notificator.onCurrentHintEnd)

    @staticmethod
    def loadValidateHintActions(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            HintActionName = record.get("HintActionName")
            isHint = bool(record.get("isHint"))

            if isHint is True:
                HintManager.s_validateHintTypes.append(HintActionName)

    @staticmethod
    def loadSceneExceptions(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            ExceptionID = record.get("ExceptionID")
            MindID = record.get("MindID")

            HintManager.s_sceneExceptions[ExceptionID] = MindID

    @staticmethod
    def loadBlackList(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            ObjectName = record.get("ObjectName")
            GroupName = record.get("GroupName")

            Object = GroupManager.getObject(GroupName, ObjectName)

            HintManager.s_blackList.append(Object)

    @staticmethod
    def inBlackList(object_):
        return object_ in HintManager.s_blackList

    @staticmethod
    def hasSceneException(exceptionID):
        return exceptionID in HintManager.s_sceneExceptions

    @staticmethod
    def getSceneExceptionMindID(exceptionID):
        return HintManager.s_sceneExceptions[exceptionID]

    @staticmethod
    def importHintActions(module, names):
        for name in names:
            HintManager.importHintAction(module, name)

    @staticmethod
    def importHintAction(module, name):
        Name = "%s" % name
        FromName = module
        ModuleName = "%s.%s" % (FromName, Name)
        Module = __import__(ModuleName, fromlist=[FromName])
        Type = getattr(Module, Name)
        HintManager.addHintAction(name, Type)

    @staticmethod
    def setMask(mask):
        HintManager.s_mask = mask

    @staticmethod
    def clearMask():
        HintManager.s_mask = None

    @staticmethod
    def getHintPriority(hintType):
        hint = HintManager.s_hintTypes[hintType]
        return hint.getPriority()

    @staticmethod
    def addHintAction(actionType, action):
        HintManager.s_actions[actionType] = action

    @staticmethod
    def hasHintActionType(questType):
        return questType in HintManager.s_questsType

    @staticmethod
    def getHintActionType(questType):
        return HintManager.s_questsType[questType]

    @staticmethod
    def isValidateHint(hintActionType):
        return hintActionType in HintManager.s_validateHintTypes

    @staticmethod
    def getHintAction(actionType):
        action = HintManager.s_actions[actionType]
        return action

    @staticmethod
    def createHintAction(hintActionType, quest, **params):
        hintAction = HintManager.getHintAction(hintActionType)
        if hintAction is None:
            return None

        hintAction = hintAction()
        hintAction.setType(hintActionType)
        hintAction.onParams(params)
        hintAction.setQuest(quest)
        hintAction.onInitialize()

        return hintAction

    @staticmethod
    def __findHint(questCache, Hint, checkActive=True):
        currentSceneName = SceneManager.getCurrentSceneName()
        hintActions = []

        if questCache is None:
            return None

        for quest in questCache:
            # hint action pre-validation
            if checkActive is True:
                if quest.active is False:
                    continue
            if quest.isComplete() is True:
                continue
            if quest.isTechnical is True:
                continue
            if quest.questType not in HintManager.s_hintTypes:
                continue

            # creating hint action (3 variants)
            if quest.questType == "EnterZoom":
                ZoomGroupName = quest.params.get("GroupName")
                zoom = ZoomManager.getZoom(ZoomGroupName)
                if zoom.hasObject() is False:
                    continue
                ZoomObject = ZoomManager.getZoomObject(ZoomGroupName)
                Params = dict(Zoom=ZoomObject)
                hintAction = HintManager.createHintAction("HintActionZoom", quest, **Params)

            elif quest.questType == "EnterScene":
                HintSceneName = quest.params.get("SceneName")
                currentSceneName = SceneManager.getCurrentSceneName()
                TransitionObject = TransitionManager.findTransitionObjectToScene(currentSceneName, HintSceneName)

                if TransitionObject is not None:
                    Params = dict(Transition=TransitionObject)
                    hintAction = HintManager.createHintAction("HintActionTransition", quest, **Params)
                else:
                    TransitionBack = TransitionManager.findTransitionBackToScene(currentSceneName, HintSceneName)
                    if TransitionBack is not None:
                        Params = dict(Transition=TransitionBack)
                        hintAction = HintManager.createHintAction("HintActionTransitionBack", quest, **Params)
                    else:
                        continue
            else:
                hintActionType = HintManager.getHintActionType(quest.questType)
                hintAction = HintManager.createHintAction(hintActionType, quest, **quest.params)

            questSceneName = quest.params.get("SceneName")
            # hint action validation
            if checkActive is False:
                if currentSceneName == questSceneName:
                    hintActionType = hintAction.getType()
                    if hintActionType == "HintActionDummy":
                        continue

            if hintAction.onCheck() is False:
                continue

            if quest.questType == "Enigma" and questSceneName == currentSceneName:
                continue

            # if item collect is open, localQuestCache will have one quest for item collect
            # also there are other quests, but we prioritize this one among others
            # if item collect is open, we need only hint for item collect quests
            if hintAction.getType() is 'HintActionItemCollect':
                return hintAction

            hintActions.append(hintAction)

        if _DEVELOPMENT is True and "hint" in Mengine.getOptionValues("debug"):
            if len(hintActions) != 0:
                _hintActions = [(hint_action.__class__.__name__, hint_action.Quest.questType) for hint_action in hintActions]
                Trace.msg("[Hint debug] Found next hint actions: {}".format(_hintActions))

        # pick random
        countActions = len(hintActions)
        if countActions != 0:
            index = Mengine.range_rand(0, countActions)
            hintAction = hintActions[index]
            return hintAction

    @staticmethod
    def findSceneHint(sceneName, groupName, Hint, checkActive):
        localQuestsCache = QuestManager.getLocalQuests(sceneName, groupName)
        hintAction = HintManager.__findHint(localQuestsCache, Hint, checkActive)

        if hintAction is None:
            questSceneCache = QuestManager.getSceneQuests(sceneName, groupName)
            hintAction = HintManager.__findHint(questSceneCache, Hint, checkActive)

        return hintAction

    @staticmethod
    def findGlobalHint(Hint):
        questGlobalCache = QuestManager.getGlobalQuests()
        hintAction = HintManager.__findHint(questGlobalCache, Hint, True)
        return hintAction
