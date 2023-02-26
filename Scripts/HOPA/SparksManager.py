from Foundation.DatabaseManager import DatabaseManager
from Foundation.GroupManager import GroupManager
from HOPA.QuestManager import QuestManager
from HOPA.TransitionManager import TransitionManager
from HOPA.ZoomManager import ZoomManager

class SparksManager(object):
    s_questsType = {}
    s_actionTypes = {}
    s_questActions = {}
    s_effects = {}

    @staticmethod
    def onFinalize():
        SparksManager.s_questsType = {}
        SparksManager.s_actionTypes = {}
        SparksManager._actions = {}

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            QuestType = record.get("QuestType")
            ActionType = record.get("ActionType")
            EffectGroup = record.get("EffectGroup", "Sparks")
            EffectName = record.get("EffectName", "Movie2_Sparks")
            effect = GroupManager.getObject(EffectGroup, EffectName)

            SparksManager.s_questsType[QuestType] = ActionType
            SparksManager.s_effects[ActionType] = effect

        return True

    @staticmethod
    def getActionEffect(actionType):
        return SparksManager.s_effects[actionType]

    @staticmethod
    def importSparksActions(module, names):
        for name in names:
            SparksManager.importSparksAction(module, name)

    @staticmethod
    def importSparksAction(module, name):
        Name = "%s" % (name)
        FromName = module
        ModuleName = "%s.%s" % (FromName, Name)
        Module = __import__(ModuleName, fromlist=[FromName])
        Type = getattr(Module, Name)
        SparksManager.addSparksAction(name, Type)

    @staticmethod
    def addSparksAction(name, action):
        SparksManager.s_actionTypes[name] = action

    @staticmethod
    def getSparksAction(actionType):
        action = SparksManager.s_actionTypes[actionType]

        return action

    @staticmethod
    def hasSparksAction(actionType):
        if actionType in SparksManager.s_effects:
            return True

        return False

    @staticmethod
    def createSparksAction(questType, **params):
        actionType = SparksManager.s_questsType[questType]
        sparksAction = SparksManager.getSparksAction(actionType)

        if sparksAction is None:
            return None

        sparksAction = sparksAction()
        sparksAction.setType(actionType)
        sparksAction.onParams(params)
        sparksAction.onInitialize()

        return sparksAction

    @staticmethod
    def findSceneSparksAction(sceneName, groupName):
        listTypes = []
        questSceneCache = QuestManager.getSceneQuests(sceneName, groupName)
        questActions = []
        if questSceneCache is not None:
            countQuests = len(questSceneCache)
            if countQuests != 0:
                for quest in questSceneCache:
                    if quest.questType not in SparksManager.s_questsType:
                        continue

                    sparksAction = SparksManager.createSparksAction(quest.questType, **quest.params)
                    if sparksAction.onCheck() is False:
                        continue

                    questActions.append(sparksAction)

                countOfQuestActions = len(questActions)
                if countOfQuestActions != 0:
                    listTypes.append(questActions)

        openZoomGroupName = ZoomManager.getZoomOpenGroupName()
        if groupName != openZoomGroupName or len(listTypes) == 0:
            sceneTransitions = TransitionManager.getOpenSceneTransitions(sceneName)
            if len(sceneTransitions) > 0:
                if "Transition" in SparksManager.s_questsType:
                    listTypes.append(sceneTransitions)

            sceneZooms = ZoomManager.getActiveSceneZooms(sceneName)
            if len(sceneZooms) > 0:
                if "Zoom" in SparksManager.s_questsType:
                    listTypes.append(sceneZooms)

        countTypes = len(listTypes)
        if countTypes == 0:
            return None

        if countTypes == 1:
            indexType = 0
        else:
            indexType = Mengine.range_rand(0, countTypes)

        currentSparksType = listTypes[indexType]

        if currentSparksType == questActions:
            countActiveQuests = len(questActions)
            index = Mengine.range_rand(0, countActiveQuests)

            sparksAction = questActions[index]

            return sparksAction

        elif currentSparksType == sceneTransitions:
            countTransitions = len(sceneTransitions)
            indexTransition = Mengine.range_rand(0, countTransitions)
            Transition = sceneTransitions[indexTransition]
            params = dict(Transition=Transition)

            sparksAction = SparksManager.createSparksAction("Transition", **params)
            if sparksAction.onCheck() is False:
                return None

            return sparksAction

        elif currentSparksType == sceneZooms:
            countZooms = len(sceneZooms)
            indexZoom = Mengine.range_rand(0, countZooms)
            #            indexZoom = 1
            Zoom = sceneZooms[indexZoom]
            Object = Zoom.getObject()
            params = dict(Zoom=Object)
            sparksAction = SparksManager.createSparksAction("Zoom", **params)
            if sparksAction.onCheck() is False:
                return None

            return sparksAction

        return None