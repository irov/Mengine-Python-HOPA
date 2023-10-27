from Foundation.DefaultManager import DefaultManager
from Foundation.DemonManager import DemonManager
from Foundation.Notificator import Notificator
from Foundation.SceneManager import SceneManager
from Foundation.System import System
from Foundation.SystemManager import SystemManager
from Foundation.TaskManager import TaskManager
from HOPA.CruiseControlManager import CruiseControlManager
from HOPA.QuestManager import QuestManager
from HOPA.TransitionManager import TransitionManager
from HOPA.ZoomManager import ZoomManager
from Notification import Notification


CRUISE_LOGGER = None

ActionConsideredBlockedTime = DefaultManager.getDefaultFloat("CruiseControlActionConsideredBlockedTimeMs", 3000.0)
FindNewCruiseDelay = DefaultManager.getDefaultFloat("CruiseControlFindNewCruiseDelay", 250.0)
CruiseRestartDelay = DefaultManager.getDefaultFloat("CruiseControlRestartDelay", 1000.0)
CruiseControlCursorSpeed = DefaultManager.getDefaultFloat("CruiseControlCursorSpeed", 700.0)

CruiseControlActivateKey = DefaultManager.getDefaultKey("CruiseControlActivate", "VK_W")
CruiseControlActivateKeyName = DefaultManager.getDefaultKeyName("CruiseControlActivate", "VK_W")
CruiseControlDeactivateKey = DefaultManager.getDefaultKey("CruiseControlDeactivate", "VK_E")
CruiseControlDeactivateKeyName = DefaultManager.getDefaultKeyName("CruiseControlDeactivate", "VK_E")

Autoplay = DefaultManager.getDefaultBool("Autoplay", False)

CruiseControlTestHint = DefaultManager.getDefaultBool("CruiseControlTestHint", False)


# todo: add variable to control if cruise skips cutscenes
# todo: add random cruise action picking

# DEPRECATED
CruiseControlSpeedFactor = DefaultManager.getDefaultFloat("CruiseControlGameSpeedFactor", 1.0)


def MAKE_CRUISE_LOG():
    global CRUISE_LOGGER

    if not CRUISE_LOGGER:
        t = Mengine.getDatePathTimestamp()
        cruiseLogName = "Cruise_%s.log" % t
        CRUISE_LOGGER = Mengine.makeFileLogger(cruiseLogName)


def __LOG_TIMESTAMP_MSG(msg):
    timestamp = Mengine.getLoggerTimestamp("[%02u:%02u:%02u:%04u]")

    return "%s %s" % (timestamp, msg)


def CRUISE_LOG(msg):
    if CRUISE_LOGGER:
        CRUISE_LOGGER(msg)


class SystemCruiseControl(System):
    def __init__(self):
        super(SystemCruiseControl, self).__init__()
        self.currentAction = None

        self.isTurnOn = False

        self.guardBlockInputCount = 0
        self.debug_cruise_give = _DEVELOPMENT is True and "cruise" in Mengine.getOptionValues("debug")

    def _onRun(self):
        # todo: on popup restart fix cruise blocker (probably block input counter)
        # todo: make force restart on block input if time > 10 sec
        # todo: hack make popup window ignore block input

        if Autoplay is False:
            return True

        self.addObserver(Notificator.onKeyEvent, self.__ButtonPressedObserver)
        self.addObserver(Notificator.onPopupMessageShow, self.__PopupMessageShowObserver)
        self.addObserver(Notificator.onSceneChange, self.__SceneChangeObserver)
        self.addObserver(Notificator.onTransitionBegin, self.__TransitionBeginObserver)
        # self.addObserver(Notificator.onTaskGuardUpdate, self.__TaskGuardUpdateObserver)

        return True

    def __ButtonPressedObserver(self, key, _x, _y, isDown, _isRepeating):
        if SceneManager.isCurrentGameScene() is False:
            return False

        if SystemManager.hasSystem("SystemEditBox"):
            system_edit_box = SystemManager.getSystem("SystemEditBox")
            if system_edit_box.hasActiveEditbox():
                return False

        if isDown is True:
            if key == CruiseControlActivateKey and self.isTurnOn is False:
                self.isTurnOn = True
                self.__restartCruiseControl_Delayed()
                self._debugCruisetLog(
                    "Cruise Activated. Press {!r} to Deactivate.".format(CruiseControlDeactivateKeyName))

            elif key == CruiseControlDeactivateKey and self.isTurnOn is True:
                self.isTurnOn = False
                self.__stopCruiseControl()
                self._debugCruisetLog(
                    "Cruise Deactivated. Press {!r} to Activate.".format(CruiseControlActivateKeyName))
        return False

    def __PopupMessageShowObserver(self, text_id):
        if self.isTurnOn:
            # print "__PopupMessageShowObserver __stopCruiseControl"
            self.__stopCruiseControl()

            scene = SceneManager.getCurrentSceneName()
            group = SceneManager.getSceneMainGroupName(scene)

            quest = QuestManager.createLocalQuest('Message', SceneName=scene, GroupName=group)

            bShouldPressYes = True if text_id == "ID_POPUP_CONFIRM_MiniGame_QUIT" else False
            cruise = CruiseControlManager.createCruiseAction("CruiseActionMessage", quest,
                                                             SelectYesChoice=bShouldPressYes)

            if cruise.onCheck():  # If Popup Window Is Active

                with TaskManager.createTaskChain(Name='CruiseControl') as tc:
                    tc.addListener(Notificator.onCruiseActionEnd)
                    # print "__PopupMessageShowObserver popup action end, __restartCruiseControl_Delayed"
                    tc.addFunction(self.__restartCruiseControl_Delayed)

                cruise.onAction()

            else:
                # print "__PopupMessageShowObserver popup check fail, __restartCruiseControl_Delayed"
                self.__restartCruiseControl_Delayed()

        return False

    def __SceneChangeObserver(self, _sceneName):
        """
            restart cruise tc on scene change
        """
        if self.isTurnOn:
            self.__stopCruiseControl()

            def _onSceneEnterRestartCruise(_sceneName):
                self.__restartCruiseControl_Delayed()

                return True

            Notification.addObserver(Notificator.onSceneEnter, _onSceneEnterRestartCruise)

        return False

    def __TransitionBeginObserver(self, *args):
        if self.isTurnOn:
            # print "__TransitionBeginObserver __stopCruiseControl()"
            self.__stopCruiseControl()

        return False

    def __TaskGuardUpdateObserver(self, bGuard):
        if bGuard:
            self.guardBlockInputCount += 1
        else:
            self.guardBlockInputCount -= 1

        if self.guardBlockInputCount != 0:
            if self.isTurnOn:
                # print "__TaskGuardUpdateObserver True __stopCruiseControl()", self.guardBlockInputCount
                self.__stopCruiseControl()
        else:
            if self.isTurnOn:
                # print "Guard Deactivated: __restartCruiseControl_Delayed", self.guardBlockInputCount

                self.__restartCruiseControl_Delayed()

        return False

    def _debugCruisetLog(self, msg):
        if self.debug_cruise_give is False:
            return
        Trace.msg("[SystemCruiseControl debug] {}".format(msg))

    def __restartCruiseControl_Delayed(self):
        if TaskManager.existTaskChain("SystemCruiseControlDelayedRestart"):
            TaskManager.cancelTaskChain("SystemCruiseControlDelayedRestart")

        with TaskManager.createTaskChain(Name="SystemCruiseControlDelayedRestart") as tc:
            tc.addDelay(CruiseRestartDelay)
            tc.addFunction(self.__startCruiseControl)

    def __stopCruiseControl(self):
        self.currentCruiseEnd()

        if TaskManager.existTaskChain("CruiseControl"):
            TaskManager.cancelTaskChain("CruiseControl")

        if TaskManager.existTaskChain("SystemCruiseControlDelayedRestart"):
            TaskManager.cancelTaskChain("SystemCruiseControlDelayedRestart")

    def __startCruiseControl(self):
        MAKE_CRUISE_LOG()

        self.currentCruiseEnd()

        if TaskManager.existTaskChain("CruiseControl"):
            TaskManager.cancelTaskChain("CruiseControl")

        with TaskManager.createTaskChain(Name="CruiseControl", Repeat=True, NoCheckAntiStackCycle=True) as tc:
            tc.addDelay(0.0)  # delay one frame

            with tc.addSwitchTask(2, self.__cruiseActionCheck) as (tc_wait, tc_ok):
                tc_wait.addDelay(0.0)  # delay one frame

                with tc_ok.addRaceTask(3) as (race_0, race_1, race_2):
                    # race_0.addListener(Notificator.onQuestEnd, Filter=self.__onQuestEndFilter)
                    # better to use this in CruiseAction types where they needed
                    race_0.addBlock()
                    race_1.addListener(Notificator.onCruiseActionEnd, Filter=self.__onCruiseEndFilter)
                    race_2.addScope(self.__checkCruiseBlocker)

                tc_ok.addFunction(self.currentCruiseEnd)
                tc_ok.addDelay(0.0)  # delay one frame

            tc.addDelay(FindNewCruiseDelay)  # temp delay for testing

    def __onCruiseEndFilter(self, cruise_action):
        # print "\t [SystemCruiseControl] cruise filter"
        # print "\t [SystemCruiseControl] CruiseEnd", cruise_action.__class__.__name__, cruise_action

        return True

    def __onQuestEndFilter(self, quest):
        # print "\t [SystemCruiseControl] quest filter"

        if self.currentAction is None:
            return False

        currentQuest = self.currentAction.getQuest()

        if quest == currentQuest:
            # print "\t [SystemCruiseControl] CruiseEnd QUEST COMPLETE", quest.getType()
            return True

        return False

    def __checkCruiseBlocker(self, source):
        source.addDelay(ActionConsideredBlockedTime)

        # print blocker:
        quest_type = None
        quest_param_name = None

        if self.currentAction and self.currentAction.Quest:
            quest_type = self.currentAction.Quest.questType

            # if blocker is animation that playing more than self.actionConsideredBlockedTime no need to log it
            if self.currentAction.getType() == "CruiseActionDummy" and quest_type == "Play":
                return

            # get param name
            obj = self.currentAction.Quest.params.get("Object", None)
            if obj:
                quest_param_name = obj.getName()
            else:
                item_name = self.currentAction.Quest.params.get("ItemName", None)
                if item_name:
                    quest_param_name = item_name
                else:
                    scene_name_to = self.currentAction.Quest.params.get("SceneNameTo", None)
                    if scene_name_to:
                        quest_param_name = scene_name_to
                    else:
                        group_name = self.currentAction.Quest.params.get("GroupName", None)
                        if group_name:
                            quest_param_name = group_name

        msg = "[SystemCruiseControl] BLOCKER: skip action %s, quest: %s, param: %s, doesn't finished after %d seconds elapsed" % (
            self.currentAction.__class__.__name__, quest_type, quest_param_name, int(ActionConsideredBlockedTime / 1000.0))

        source.addFunction(CRUISE_LOG, msg)

    def __cruiseActionCheck(self, isSkip, cb):
        self.currentAction = self.__getCruiseAction()

        if self.currentAction is not None:
            if self.currentAction.onCheck():
                cb(isSkip, 1)

                if CruiseControlTestHint:
                    SystemManager.getSystem("SystemHint").showHintEvent(cb=self.currentAction.onAction)
                else:
                    self.currentAction.onAction()
                    # print "__cruiseActionCheck onAction: {}".format(self.currentAction.__class__.__name__)
                return

            else:
                # print "__cruiseActionCheck onCHeckfail: {}".format(self.currentAction.__class__.__name__)
                cb(isSkip, 0)

        else:
            # print "__cruiseActionCheck onCHeckfail: self.cruiseAction is NOne"
            cb(isSkip, 0)

    def currentCruiseEnd(self):
        if self.currentAction is not None:
            # print "[SystemCruiseControl] currentCruiseEnd"
            self.currentAction.onEnd()
            self.currentAction = None

    def __getCruiseAction(self):
        # print "__getCruiseAction"

        CruiseAction = CruiseControlManager.findGlobalCruise()

        if CruiseAction is not None:
            quest = CruiseAction.getQuest()
            if quest is not None:
                self._debugCruisetLog("[1] Global Quest Type {}".format(quest.getType()))
            else:
                self._debugCruisetLog("[1] Global Cruise Type {}".format(CruiseAction.getType()))
            # print "__getCruiseAction Global"
            return CruiseAction

        currentSceneName = SceneManager.getCurrentSceneName()
        groupName = SceneManager.getSceneMainGroupName(currentSceneName)

        zoomGroupName = ZoomManager.getZoomOpenGroupName()

        CruiseAction = self.getItemPlusCruiseAction(currentSceneName)
        if CruiseAction is not None:
            # print "__getCruiseAction PlusScene: {}".format(CruiseAction.__class__.__name__)
            # print "__getCruiseAction ItemPlus"
            quest = CruiseAction.getQuest()
            if quest is not None:
                self._debugCruisetLog("[2] ItemPlus Quest Type {}".format(quest.getType()))
            else:
                self._debugCruisetLog("[2] ItemPlus Cruise Type {}".format(CruiseAction.getType()))
            # print "__getCruiseAction Global"
            return CruiseAction

        if zoomGroupName is not None:
            # print "ZoomGroup is not None"

            CruiseAction = CruiseControlManager.findSceneCruise(currentSceneName, zoomGroupName, True)
            # print "__getCruiseAction (zoom group is not None) Scene"
            if CruiseAction is not None:
                quest = CruiseAction.getQuest()
                quest_type = None
                if quest is not None:
                    quest_type = quest.getType()

                self._debugCruisetLog(
                    "[3] Zoom Scene. Cruise Type {}, Quest type {}, SceneName {}, GroupName {}".format(
                        CruiseAction.getType(), quest_type, currentSceneName, zoomGroupName))
                return CruiseAction

            CruiseAction = self.getSceneCruiseAction(currentSceneName, groupName)
            if CruiseAction is not None:
                # print "__getCruiseAction (zoom group is not None) ZoomLeave"
                self._debugCruisetLog("[4] CurrentSceneCheck ZoomLeave, created ZoomLeaveCruiseAction: {} {}".format(
                    CruiseAction.__class__.__name__, CruiseAction.Quest))
                return self.createZoomLeaveCruiseAction(zoomGroupName)

            CruiseSceneName, CruiseAction = self.getAroundSceneCruiseAction(currentSceneName, True)

            if CruiseAction is not None:
                TransitionObject = TransitionManager.findTransitionObjectToScene(currentSceneName, CruiseSceneName)

                if TransitionObject is not None and TransitionObject.getGroupName() == zoomGroupName:
                    CruiseAction = self.createSceneEnterCruiseAction(TransitionObject)
                    if CruiseAction is not None:
                        self._debugCruisetLog("[5] AroundSceneCheck, created SceneEnterCruiseAction: {} {}".format(
                            CruiseAction.__class__.__name__, CruiseAction.Quest))
                        # print "__getCruiseAction (zoom group is not None) sceneEnter(TransitionObj)"
                        return CruiseAction

            CruiseAction = self.createZoomLeaveCruiseAction(zoomGroupName)
            self._debugCruisetLog("[6] AroundSceneCheck ZoomLeave, created ZoomLeaveCruiseAction: {} {}".format(
                CruiseAction.__class__.__name__, CruiseAction.Quest))
            # print "__getCruiseAction (zoom group is not None) zoomLeave"
            return CruiseAction

        else:
            # print "ZoomGroup is None"

            # try get item collect cruise action
            cruiseAction = self.getItemCollectCruiseAction(currentSceneName)
            if cruiseAction is not None:
                self._debugCruisetLog("[7] CollectItemSceneCheck, create ItemCollectCruiseAction: {} {}".format(
                    cruiseAction.__class__.__name__, cruiseAction.Quest))
                # print "__getCruiseAction ItemCollect"
                return cruiseAction

            CruiseAction = self.getSceneCruiseAction(currentSceneName, groupName)
            if CruiseAction is not None:
                quest = CruiseAction.getQuest()
                quest_type = None
                if quest is not None:
                    quest_type = quest.getType()

                self._debugCruisetLog("[8] Scene. Cruise Type {}, Quest type {}, SceneName {}, GroupName {}".format(
                    CruiseAction.getType(), quest_type, currentSceneName, zoomGroupName))
                # print "__getCruiseAction (zoom is None) Scene"
                return CruiseAction

            cruiseAction = self.getZoomCruiseAction(currentSceneName)
            if cruiseAction is not None:
                self._debugCruisetLog("[9] ZoomCheck, CreateZoomEnterCruiseAction: {} {}".format(
                    cruiseAction.__class__.__name__, cruiseAction.Quest))
                # print "__getCruiseAction (zoom is None) ZoomEnter"
                return cruiseAction

            CruiseSceneName, CruiseActionAroundScene = self.getAroundSceneCruiseAction(currentSceneName, True)
            if CruiseActionAroundScene is not None:
                TransitionObject = TransitionManager.findTransitionObjectToScene(currentSceneName, CruiseSceneName)

                if TransitionObject is not None:
                    if TransitionObject.active is False:
                        TransitionGroupName = TransitionObject.getGroupName()

                        cruiseAction = self.createZoomEnterCruiseAction(currentSceneName, TransitionGroupName, False)
                        if cruiseAction is not None:
                            self._debugCruisetLog("[10] CreateZoomEnterCruiseAction: {} {}".format(
                                cruiseAction.__class__.__name__, cruiseAction.Quest))
                            # print "__getCruiseAction (zoom is None) (transition obj is not None) ZoomEnter"
                            return cruiseAction

                    else:
                        CruiseAction = self.createSceneEnterCruiseAction(TransitionObject)
                        if CruiseAction is not None:
                            self._debugCruisetLog("[11] CreateSceneEnterCruiseAction: {} {}".format(
                                CruiseAction.__class__.__name__, CruiseAction.Quest))
                            # print "__getCruiseAction (zoom is None) (trans obj is not None) (trans obj is Active) SceneEnter"
                            return CruiseAction
                        else:
                            self._debugCruisetLog("[11] CreateSceneEnterCruiseAction: {} {} FAILED".format(
                                currentSceneName, TransitionObject))

                elif TransitionManager.hasTransitionBack(currentSceneName) is True:
                    TransitionBackObject = TransitionManager.getTransitionBackObject()

                    CruiseAction = self.createSceneEnterCruiseAction(TransitionBackObject)
                    if CruiseAction is not None:
                        self._debugCruisetLog("[12] CreateSceneEnterCruiseAction: {} {}".format(
                            CruiseAction.__class__.__name__, CruiseAction.Quest))
                        # print "__getCruiseAction (zoom is None) (trans obj is None) TransitionBack"
                        return CruiseAction
                    else:
                        self._debugCruisetLog("[12] CreateSceneEnterCruiseAction: {} FAILED".format(currentSceneName))

    def getSceneCruiseAction(self, sceneName, groupName, checkActive=True):
        """
        Cruise Manager main method for cruiseAction creation wrapper

        @param sceneName - action place partial identifier
        @param groupName - action place partial identifier
        @param checkActive - if true check for actions we able to complete
        """
        return CruiseControlManager.findSceneCruise(sceneName, groupName, checkActive)

    @staticmethod
    def getItemCollectCruiseAction(sceneName):
        if SystemManager.hasSystem("SystemItemCollect") is False:
            return

        currentActiveItemCollectName = SystemManager.getSystem("SystemItemCollect").getCurrentItemCollect()

        if currentActiveItemCollectName is not None:  # has opened ItemCollect create itemCollect placeItem action
            itemCollects = SystemManager.getSystem("SystemItemCollect").getItemList()

            itemCollect = itemCollects[currentActiveItemCollectName]

            Quest = QuestManager.createLocalQuest('ItemCollect', SceneName=currentActiveItemCollectName[0],
                                                  GroupName=currentActiveItemCollectName[0], ItemList=itemCollect[0],
                                                  Object=itemCollect[1])

            return CruiseControlManager.createCruiseAction('CruiseActionItemCollect', Quest,
                                                           SceneName=currentActiveItemCollectName[0],
                                                           GroupName=currentActiveItemCollectName[0],
                                                           ItemList=itemCollect[0], Object=itemCollect[1])

        else:  # has closed ItemCollect create open ItemCollect
            itemCollects = SystemManager.getSystem("SystemItemCollect").getItemList()

            for (ItemCollectSceneName, SocketName), (item_list, socket, flag) in itemCollects.iteritems():
                if sceneName != ItemCollectSceneName:
                    continue

                if flag is True:
                    continue

                Quest = QuestManager.createLocalQuest("ItemCollectOpen", SceneName=sceneName, GroupName=sceneName,
                                                      Object=socket)

                return CruiseControlManager.createCruiseAction('CruiseActionClick', Quest, SceneName=sceneName,
                                                               GroupName=sceneName, Object=socket)

    def getSpellUseCruiseAction(self, sceneName):
        if SystemManager.hasSystem("SystemSpells") is False:
            return

        SystemSpells = SystemManager.getSystem("SystemSpells")
        SpellUIComponents = SystemSpells.getSpellUIComponents()

        for UIComponent in SpellUIComponents.values():
            if UIComponent.hasSceneActiveQuest() is True:
                Quests = UIComponent.getSceneActiveQuests()
                power_name = Quests[0].params['PowerName']
                return CruiseControlManager.createCruiseAction('CruiseActionSpellAmuletUseRune', Quests[0],
                                                               Power_Name=power_name)

    def getZoomCruiseAction(self, sceneName):
        if SceneManager.hasSceneZooms(sceneName) is False:
            return

        zooms = SceneManager.getSceneZooms(sceneName)

        for zoomGroupName in zooms:
            hasSceneActiveQuest = QuestManager.hasAroundSceneQuest(sceneName, zoomGroupName)
            if hasSceneActiveQuest is False:
                continue

            cruiseAction = self.createZoomEnterCruiseAction(sceneName, zoomGroupName)
            if cruiseAction is None:
                continue

            return cruiseAction

    def getItemPlusCruiseAction(self, currentSceneName):
        if SystemManager.hasSystem("SystemItemPlusScene"):
            if SystemManager.getSystem("SystemItemPlusScene").Open_Zoom is not None:
                return self.getItemPlusCruiseAction_SceneCruise(currentSceneName)

            else:
                return self.getItemPlusCruiseAction_ClickOpen(currentSceneName)

    def getItemPlusCruiseAction_SceneCruise(self, currentSceneName):
        if SystemManager.hasSystem("SystemItemPlusScene"):
            ScenePlus = SystemManager.getSystem("SystemItemPlusScene").Open_Zoom[1]
            groupScenePlusName = SceneManager.getSceneMainGroupName(ScenePlus)

            # scene plus cruise
            cruiseAction = self.getSceneCruiseAction(ScenePlus, groupScenePlusName, True)

            if cruiseAction is None:  # if no scene plus cruise - create cruise action leave scene plus
                return CruiseControlManager.createCruiseAction("CruiseActionPlusSceneOut", None)
            else:
                return cruiseAction

    @staticmethod
    def getItemPlusCruiseAction_ClickOpen(currentSceneName):
        if SystemManager.hasSystem("SystemItemPlusScene") is False:
            return

        Inventory = DemonManager.getDemon("Inventory")
        if Inventory is None:
            return

        if Inventory.isActive() is False:
            return

        plus_Items = SystemManager.getSystem("SystemItemPlusScene").items_Inventort

        for key, val in plus_Items.iteritems():
            ItemClick = val[0]
            ScenePlus = val[2].PlusScene
            groupName = SceneManager.getSceneMainGroupName(ScenePlus)

            hasSceneActiveQuest = QuestManager.hasAroundSceneQuest(ScenePlus, groupName)

            if hasSceneActiveQuest is False:
                continue

            Inventory = DemonManager.getDemon("Inventory")

            if Inventory.hasInventoryItem(ItemClick) is False:
                continue

            Params = dict(InventoryItem=ItemClick)

            if QuestManager.hasLocalQuest(currentSceneName, groupName, "Click") is True:
                Quest = QuestManager.getSceneQuest(currentSceneName, groupName, "Click")

            else:
                Quest = QuestManager.createLocalQuest("Click", SceneName=ScenePlus, GroupName=groupName)

                with TaskManager.createTaskChain() as tc:
                    with QuestManager.runQuest(tc, Quest) as tc_quest:
                        def _filter(scene):
                            if scene == ScenePlus:
                                return True

                            return False

                        tc_quest.addTask("TaskListener", ID=Notificator.onSceneEnter, Filter=_filter)

            return CruiseControlManager.createCruiseAction("CruiseActionPlusScene", Quest, **Params)

    def getAroundSceneCruiseAction(self, fromSceneName, checkActive=False):
        aroundScenes = TransitionManager.findSpiralScenes(fromSceneName)

        for sceneName in aroundScenes[1:]:
            groupName = SceneManager.getSceneMainGroupName(sceneName)

            hasSceneActiveQuest = QuestManager.hasAroundSceneQuest(sceneName, groupName)

            if hasSceneActiveQuest is not False:
                cruiseAction = self.getSceneCruiseAction(sceneName, groupName, False)

                if cruiseAction is not None:
                    if checkActive is True:
                        TransitionObject = TransitionManager.findTransitionObjectToScene(fromSceneName, sceneName)

                        if TransitionObject is not None:
                            return sceneName, cruiseAction

            zooms = SceneManager.getSceneZooms(sceneName)

            if zooms is None:
                continue

            for zoomGroupName in zooms:
                cruiseAction = CruiseControlManager.findSceneCruise(sceneName, zoomGroupName, False)
                if cruiseAction is None:
                    continue

                cruiseAction = self.createZoomEnterCruiseAction(sceneName, zoomGroupName, True)

                if cruiseAction is not None:
                    return sceneName, cruiseAction

        return None, None

    @staticmethod
    def createSceneEnterCruiseAction(TransitionObject):
        if TransitionObject is None:
            return

        Params = dict(Transition=TransitionObject)
        SceneNameTo = TransitionManager.getTransitionSceneTo(TransitionObject)
        GroupNameTo = SceneManager.getSceneMainGroupName(SceneNameTo)

        if SceneNameTo is None:
            return

        # create quest
        if QuestManager.hasLocalQuest(SceneNameTo, GroupNameTo, "EnterScene") is True:
            Quest = QuestManager.getSceneQuest(SceneNameTo, GroupNameTo, "EnterScene")

        else:
            Quest = QuestManager.createLocalQuest("EnterScene", SceneName=SceneNameTo, GroupName=GroupNameTo,
                                                  Transition=TransitionObject)
            with TaskManager.createTaskChain() as tc:
                with QuestManager.runQuest(tc, Quest) as tc_quest:
                    tc_quest.addTask("TaskSceneEnter", SceneName=SceneNameTo)

        # create cruise action
        if TransitionObject.getName() == "Transition_Back":
            if Mengine.hasTouchpad():
                return CruiseControlManager.createCruiseAction("CruiseActionTransitionBackMobile", Quest, **Params)
            return CruiseControlManager.createCruiseAction("CruiseActionTransitionBack", Quest, **Params)
        else:
            return CruiseControlManager.createCruiseAction("CruiseActionTransition", Quest, **Params)

    def createZoomEnterCruiseAction(self, sceneName, zoomGroupName, check=True):
        if SystemManager.hasSystem("SystemItemPlusScene"):
            if SystemManager.getSystem("SystemItemPlusScene").Open_Zoom is not None:
                # print "CANT OPEN ZOOM IF ITEM PLUS SCENE"
                return

        zoom = ZoomManager.getZoom(zoomGroupName)

        if zoom.hasObject() is False:
            return

        ZoomObject = ZoomManager.getZoomObject(zoomGroupName)
        if QuestManager.hasLocalQuest(sceneName, zoomGroupName, "EnterZoom") is True:
            Quest = QuestManager.getSceneQuest(sceneName, zoomGroupName, "EnterZoom")

        else:
            Quest = QuestManager.createLocalQuest("EnterZoom", Zoom=ZoomObject,
                                                  GroupName=zoomGroupName, SceneName=sceneName)

        Params = dict(Zoom=ZoomObject)

        cruiseAction = CruiseControlManager.createCruiseAction("CruiseActionZoom", Quest, **Params)

        if cruiseAction.onCheck() is False:
            QuestManager.cancelQuest(Quest)
            return

        if QuestManager.hasLocalQuest(sceneName, zoomGroupName, "EnterZoom") is False:
            currentSceneName = SceneManager.getCurrentSceneName()

            with TaskManager.createTaskChain() as tc:
                with QuestManager.runQuest(tc, Quest) as tc_quest:
                    with tc_quest.addRaceTask(2) as (tc_zoom, tc_scene):
                        tc_zoom.addTask("TaskZoomEnter", ZoomName=zoomGroupName, SceneName=sceneName)
                        tc_scene.addTask("TaskSceneLeave", SceneName=currentSceneName)

        if check is False:
            return cruiseAction

        hasZoomActiveQuest = QuestManager.hasAroundSceneQuest(sceneName, zoomGroupName)

        if hasZoomActiveQuest is True:
            groupName = zoomGroupName

            return self.getSceneCruiseAction(sceneName, groupName, False)

    @staticmethod
    def createZoomLeaveCruiseAction(zoomGroupName):
        currentSceneName = SceneManager.getCurrentSceneName()
        Quest = QuestManager.createLocalQuest("CloseZoom", GroupName=zoomGroupName, SceneName=currentSceneName)

        with TaskManager.createTaskChain() as tc:
            with QuestManager.runQuest(tc, Quest) as tc_quest:
                with tc_quest.addRaceTask(2) as (tc_zoom, tc_scene):
                    tc_zoom.addTask("TaskZoomLeave", ZoomName=zoomGroupName, SceneName=currentSceneName)
                    tc_scene.addTask("TaskSceneLeave", SceneName=currentSceneName)

        return CruiseControlManager.createCruiseAction("CruiseActionZoomOut", Quest)
