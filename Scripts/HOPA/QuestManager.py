from Foundation.DatabaseManager import DatabaseManager
from HOPA.ScenarioManager import ScenarioManager

from Notification import Notification


class QuestManager(object):
    s_enumerate = 0
    s_questGlobalCache = []
    s_questLocalCache = {}
    s_questsTypes = {}

    s_activeTipObjects = []

    onQuestRunObserver = None
    onQuestEndObserver = None

    class QuestObject(object):
        __slots__ = "questType", "params", "questGlobal", "active", "complete", "isTechnical"

        if _DEVELOPMENT is True and "quest" in Mengine.getOptionValues("debug"):
            def __repr__(self):
                MacroCommand = self.params.get("FromMacroCommand")
                _details = [
                    ("A" if self.active else "N/A"),
                    ("GLOBAL" if self.questGlobal else "LOCAL"),
                    ("Done" if self.complete else "Work"),
                ]
                details = " ".join(_details)
                return "<QuestObject {} [{}] from {}: {}>".format(self.questType, details, MacroCommand, self.params)

        def __init__(self, questType, params, questGlobal, Technical):
            self.questType = questType
            self.params = params
            self.questGlobal = questGlobal
            self.active = False
            self.complete = False
            self.isTechnical = Technical

        def isGlobal(self):
            return self.questGlobal

        def getType(self):
            return self.questType

        def isComplete(self):
            return self.complete

        def isActive(self):
            return self.active

        def setComplete(self, value):
            self.complete = value

        def setActive(self, value):
            self.active = value

    @staticmethod
    def printQuest(quest):
        print("QuestManager printQuest, group", quest.questType, quest.params.get("GroupName"), "complete",
        quest.isComplete(), "active", quest.active, "params", quest.params)
        if quest.questType == "Click" or quest.questType == "Enable":
            print(quest.params.get("Object").name)
        elif quest.questType == "PickItem":
            print(quest.params.get("ItemName"))
        elif quest.questType == "UseInventoryItem":
            print(quest.params.get("InventoryItem").name, quest.params.get("Object").name)
        elif quest.questType == "UseHOGFittingItem":
            print(quest.params.get("InventoryItem").name, quest.params.get("Object").name)
        elif quest.questType == "RunParagraph":
            print(quest.params.get("ParagraphsID"))
        elif quest.questType == "Combine":
            print(quest.params.get("AttachInventoryItem"), quest.params.get("SlotInventoryItem"))

    @staticmethod
    def hasActiveTipObject(obj):
        if obj in QuestManager.s_activeTipObjects:
            return True
        return False

    @staticmethod
    def appendActiveTipObjects(obj):
        QuestManager.s_activeTipObjects.append(obj)

    @staticmethod
    def removeActiveTipObjects(obj):
        QuestManager.s_activeTipObjects.remove(obj)

    @staticmethod
    def onInitialize():
        QuestManager.onQuestRunObserver = Notification.addObserver(Notificator.onQuestRun, QuestManager._onAppendQuestList)
        QuestManager.onQuestEndObserver = Notification.addObserver(Notificator.onQuestEnd, QuestManager._onRemoveQuestList)

    @staticmethod
    def onFinalize():
        Notification.removeObserver(QuestManager.onQuestRunObserver)
        Notification.removeObserver(QuestManager.onQuestEndObserver)

    @staticmethod
    def _onAppendQuestList(quest):
        quest.setActive(True)
        return False

    @staticmethod
    def _onRemoveQuestList(quest):
        if quest is None:
            return False

        if QuestManager.isGlobalQuest(quest.questType) is False:
            sceneName = quest.params.get("SceneName")
            groupName = quest.params.get("GroupName")

            key = (sceneName, groupName)

            if key not in QuestManager.s_questLocalCache:
                return False

            if quest in QuestManager.s_questLocalCache[key]:
                QuestManager.s_questLocalCache[key].remove(quest)
            if len(QuestManager.s_questLocalCache[key]) == 0:
                del QuestManager.s_questLocalCache[key]

        else:
            if quest in QuestManager.s_questGlobalCache:
                QuestManager.s_questGlobalCache.remove(quest)
        return False

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            QuestType = record.get("QuestType")
            Global = bool(record.get("Global"))

            QuestManager.s_questsTypes[QuestType] = Global

        QuestManager.s_questsTypes["Dummy"] = 0

        return True

    @staticmethod
    def isGlobalQuest(questType):
        if questType not in QuestManager.s_questsTypes:
            Trace.log("Manager", 0, "QuestManager isGlobalQuest: questType [%s] not add in Quests.xls" % (questType))
            return None

        isGlobal = QuestManager.s_questsTypes[questType]

        return isGlobal

    @staticmethod
    def getGlobalQuests():
        if len(QuestManager.s_questGlobalCache) == 0:
            return None

        GlobalCache = QuestManager.s_questGlobalCache

        return GlobalCache

    @staticmethod
    def hasLocalQuest(sceneName, groupName, type):
        key = (sceneName, groupName)

        if key not in QuestManager.s_questLocalCache:
            return False

        quests = QuestManager.s_questLocalCache[key]

        for quest in quests:
            if quest.questType == type and quest.isComplete() is False and quest.active is True:
                return True

        return False

    @staticmethod
    def getSceneQuest(sceneName, groupName, type):
        key = (sceneName, groupName)
        quests = QuestManager.s_questLocalCache[key]

        for quest in quests + QuestManager.s_questGlobalCache:
            if quest.questType == type and quest.isComplete() is False and quest.active is True:
                return quest

        return None

    @staticmethod
    def __questVisitorHasActiveGiveItem(quest, type_, inventoryItem, obj):
        if quest.questType != type_:
            return None  # keep looking

        InvItem = quest.params.get("InventoryItem")
        PlaceObject = quest.params.get("Object")
        if InvItem == inventoryItem and obj == PlaceObject:
            if quest.active is False:
                return None  # keep looking

            return False  # mean questVisitor found quest

    @staticmethod
    def hasActiveGiveItem(sceneName, groupName, type_, inventoryItem, obj):
        scenarios = ScenarioManager.getSceneRunScenarios(sceneName, groupName)

        for scenarioRunner in scenarios:
            scenario = scenarioRunner.getScenario()
            paragraphs = scenario.getParagraphs()
            for paragraph in paragraphs:
                result = paragraph.visitQuests(QuestManager.__questVisitorHasActiveGiveItem, False, type_, inventoryItem, obj)
                if result is False:  # quest visitor found one, no need to look farther
                    return True
        return False  # quest visitor not found quest

    @staticmethod
    def __questVisitorAppendObjectActiveQuestGiveItem(quest, type_, obj, filter_complete, out_quest_list):
        if quest.questType != type_:
            return  # keep looking

        PlaceObject = quest.params.get("Object")
        if obj == PlaceObject and quest.active:
            if filter_complete and quest.complete:
                return

            out_quest_list.append(quest)

    @staticmethod
    def getObjectActiveGiveItemQuestList(sceneName, groupName, type_, obj, filterComplete=True):
        quest_list_in = []

        scenarios = ScenarioManager.getSceneRunScenarios(sceneName, groupName)

        for scenarioRunner in scenarios:
            scenario = scenarioRunner.getScenario()
            paragraphs = scenario.getParagraphs()

            for paragraph in paragraphs:
                paragraph.visitQuests(QuestManager.__questVisitorAppendObjectActiveQuestGiveItem, False, type_, obj, filterComplete, quest_list_in)

        return quest_list_in

    @staticmethod
    def getActiveItemQuests(sceneName, groupName, types):
        result = []
        quests = QuestManager.getSceneQuests(sceneName, groupName)
        if len(quests) == 0:
            return result
        for quest in quests:
            if quest.questType in types:
                if quest.isComplete() is True or quest.active is False:
                    continue
                result.append(quest)

        return result

    @staticmethod
    def __questVisitorGetSceneNotCompletedQuests(quest, quest_list):
        if quest.isComplete() is False:
            quest_list.append(quest)

    @staticmethod
    def getSceneQuests(sceneName, groupName):
        scenarios = ScenarioManager.getSceneRunScenarios(sceneName, groupName)
        quests = []

        for scenarioRunner in scenarios:
            scenario = scenarioRunner.getScenario()
            paragraphs = scenario.getRunParagraphs()
            for paragraph in paragraphs:
                paragraph.visitQuests(QuestManager.__questVisitorGetSceneNotCompletedQuests, False, quests)
        return quests

    @staticmethod
    def __questVisitorGetSceneAllQuests(quest, quest_list):
        quest_list.append(quest)

    @staticmethod
    def getSceneAllQuests(sceneName, groupName):
        scenarios = ScenarioManager.getSceneRunScenarios(sceneName, groupName)
        quests = []

        for scenarioRunner in scenarios:
            scenario = scenarioRunner.getScenario()
            paragraphs = scenario.getParagraphs()
            for paragraph in paragraphs:
                paragraph.visitQuests(QuestManager.__questVisitorGetSceneAllQuests, False, quests)
        return quests

    @staticmethod
    def getLocalQuests(sceneName, groupName):
        key = (sceneName, groupName)

        if key not in QuestManager.s_questLocalCache:
            return []

        quests = QuestManager.s_questLocalCache[key]

        return quests

    @staticmethod
    def __questVisitorFindOneQuestWeCanFinish(quest):
        """
            None: mean this quest is complete, check next quest in current paragraph

            True: we can't finish quest of this paragraph for now(action blocked),
            check next paragraph or if it's race/parallel, check thread in current paragraph

            False: there are quest we can complete. After return false, hasAroundSceneQuest will return True
        """
        from HOPA.HintManager import HintManager

        if quest.complete is True:
            return None
        if quest.isTechnical is True:
            return True

        action_type = HintManager.getHintActionType(quest.questType)
        hint_action = HintManager.createHintAction(action_type, quest, **quest.params)

        if hint_action.onCheck() is False:
            return True
        return False

    @staticmethod
    def hasAroundSceneQuest(scene_name, group_name, *_):
        '''
        Algorithm description:
            we take scene and group name pair (mostly it's ZOOM's)
            and for each paragraph with state=RUN we check if there are quest
            which we can complete if we found such no point of looping further,
            return True. Else we check next paragraph with state=RUN for current
            scenario(for example 05_PuppysZoom). If nothing was finded -> return False
        '''
        scenarios = ScenarioManager.getSceneRunScenarios(scene_name, group_name)

        for scenario_runner in scenarios:
            scenario = scenario_runner.getScenario()
            paragraphs = scenario.getRunParagraphs()
            for paragraph in paragraphs:
                if paragraph.visitQuests(QuestManager.__questVisitorFindOneQuestWeCanFinish, True) is False:
                    return True
        return False

    @staticmethod
    def checkValidQuestParams(questType, Params):
        if questType not in QuestManager.s_questsTypes:
            Trace.log("Manager", 0, "QuestManager checkValidQuestParams quest not creating, unknown quest type [%s]" % questType)
            return False

        isGlobal = QuestManager.isGlobalQuest(questType)
        if isGlobal is True:
            return True

        sceneName = Params.get("SceneName")
        if sceneName is None:
            Trace.log("Manager", 0, "QuestManager checkValidQuestParams: quest type [%s], not creating, sceneName is None %s" % (questType, Params))
            return False

        groupName = Params.get("GroupName")
        if groupName is None:
            Trace.log("Manager", 0, "QuestManager checkValidQuestParams: quest type [%s], not creating, groupName is None %s" % (questType, Params))
            return False

        return True

    @staticmethod
    def createScenarioQuest(questType, Technical=False, **Params):
        validParams = QuestManager.checkValidQuestParams(questType, Params)

        if validParams is False:
            return None

        isGlobal = QuestManager.isGlobalQuest(questType)
        quest = QuestManager.QuestObject(questType, Params, isGlobal, Technical)
        if isGlobal is False:
            return quest

        QuestManager.s_questGlobalCache.append(quest)

        return quest

    @staticmethod
    def createLocalQuest(questType, Technical=False, **Params):
        validParams = QuestManager.checkValidQuestParams(questType, Params)
        if validParams is False:
            return None

        sceneName = Params.get("SceneName")
        groupName = Params.get("GroupName")

        key = (sceneName, groupName)

        quest = QuestManager.QuestObject(questType, Params, False, Technical)
        QuestManager.s_questLocalCache.setdefault(key, []).append(quest)

        return quest

    class QuestChain(object):
        def __init__(self, source, quest):
            self.source = source
            self.quest = quest

        def __enter__(self):
            with self.source.addRaceTask(2) as (tc_quest, tc_chain):
                tc_quest.addTask("TaskQuestRun", Quest=self.quest)

            tc_chain.complete = False

            return tc_chain

        def __exit__(self, type, value, traceback):
            if type is not None:
                return False
            self.source.addTask("TaskFunction", Fn=QuestManager.completeQuest, Args=(self.quest, True))

            return True

    @staticmethod
    def completeQuest(quest, value):
        quest.setComplete(value)
        QuestManager.RemoveQuest(quest)

    @staticmethod
    def runQuest(source, quest):
        return QuestManager.QuestChain(source, quest)

    @staticmethod
    def RemoveQuest(quest):
        QuestManager._onRemoveQuestList(quest)

    @staticmethod
    def cancelQuest(quest):
        QuestManager._onRemoveQuestList(quest)
