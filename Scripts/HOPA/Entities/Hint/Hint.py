from Event import Event
from Foundation.DefaultManager import DefaultManager
from Foundation.DemonManager import DemonManager
from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.PolicyManager import PolicyManager
from Foundation.SceneManager import SceneManager
from Foundation.SystemManager import SystemManager
from Foundation.TaskManager import TaskManager
from HOPA.EnigmaManager import EnigmaManager
from HOPA.HintManager import HintManager
from HOPA.QuestManager import QuestManager
from HOPA.System.SystemItemCollect import SystemItemCollect
from HOPA.System.SystemItemPlusScene import SystemItemPlusScene
from HOPA.TransitionManager import TransitionManager
from HOPA.ZoomManager import ZoomManager
from Notification import Notification


class Hint(BaseEntity):

    @staticmethod
    def declareORM(Type):
        BaseEntity.declareORM(Type)
        Type.addAction(Type, "Point")
        Type.addAction(Type, "ZoomCheck")
        Type.addAction(Type, "ItemCollectCheck")
        Type.addAction(Type, "AroundSceneCheck")
        Type.addAction(Type, "AnimationSequenceCount")

    def __init__(self):
        super(Hint, self).__init__()

        self.currentHint = None
        self.blockHint = False  # enables onDialogOpen and onDialogClose observers

        # observers
        self.onSceneInitObserver = None
        self.onQuestEndObserver = None
        self.onCurrentHintEndObserver = None
        self.onItemPlusLeaveObserver = None
        self.onItemPickedObserver = None
        self.onTipActivateWithoutParagraphsObserver = None
        self.onClickItemCollectHintSocketObserver = None
        self.onDialogOpenObserver = None
        self.onDialogCloseObserver = None

        # wait till ui plays animation, then push hint
        self.waitHintUIAction = False
        self.waitNoReloadHintUIAction = False
        self.inHintPlay = False

        # policies
        self.PolicyHintClick = None
        self.PolicyHintReady = None
        self.PolicyHintReload = None
        self.PolicyHintActivate = None
        self.PolicyHintEmpty = None
        self.PolicyHintReadyInterrupt = None
        self.PolicyHintNotFound = None
        self.PolicyHintPlay = None

        self.debug_hint_give = _DEVELOPMENT is True and "hint" in Mengine.getOptionValues("debug")

        # IDK wtf is this
        self.Print = False

    def getPoint(self):
        return self.Point

    def getMovieGroup(self):
        MovieHintInDemon = DefaultManager.getDefaultBool("MovieHintInDemon", False)
        if MovieHintInDemon is True:
            MovieGroup = self.object
        else:
            MovieGroup = self.object.getGroup()

        return MovieGroup

    def _onPreparation(self):
        MovieGroup = self.getMovieGroup()

        if MovieGroup.hasObject("Movie2_Activate"):
            Movie_Activate = MovieGroup.getObject("Movie2_Activate")
            Movie_Activate.setEnable(False)

        if MovieGroup.hasObject("Movie2_Ready"):
            Movie_Ready = MovieGroup.getObject("Movie2_Ready")
            Movie_Ready.setEnable(False)

        if MovieGroup.hasObject("Movie2_Charged"):
            Movie_Charged = MovieGroup.getObject("Movie2_Charged")
            Movie_Charged.setEnable(False)

        if MovieGroup.hasObject("Movie2_Reload"):
            Movie_Reload = MovieGroup.getObject("Movie2_Reload")
            Movie_Reload.setEnable(False)

    def _onActivate(self):
        Notification.notify(Notificator.onHintActivate, self.object)
        if SystemManager.hasSystem("SystemHint") is False:
            return

        self.PolicyHintClick = PolicyManager.getPolicy("HintClick", "PolicyHintClickSocket")
        self.PolicyHintReady = PolicyManager.getPolicy("HintReady")
        self.PolicyHintReload = PolicyManager.getPolicy("HintReload")
        self.PolicyHintActivate = PolicyManager.getPolicy("HintActivate")
        self.PolicyHintEmpty = PolicyManager.getPolicy("HintEmpty")
        self.PolicyHintReadyInterrupt = PolicyManager.getPolicy("HintReadyInterrupt")
        self.PolicyHintNotFound = PolicyManager.getPolicy("HintNotFound", "PolicyHintNotFoundMind")
        self.PolicyHintPlay = PolicyManager.getPolicy("HintPlay", "PolicyHintPlayDefault")

        # run task chains:
        self.__tcHintReload()
        self.__tcHintReady()
        self.__tcHintCharge()

        self.onSceneInitObserver = Notification.addObserver(Notificator.onSceneEnter, self._onSceneInit)
        self.onQuestEndObserver = Notification.addObserver(Notificator.onQuestEnd, self._onQuestEnd)
        self.onCurrentHintEndObserver = Notification.addObserver(Notificator.onCurrentHintEnd, self.currentHintEnd)
        # self.onInventorySlotsShiftObserver = Notification.addObserver(Notificator.onInventorySlotsShiftEnd, self.currentHintEnd)
        self.onItemPlusLeaveObserver = Notification.addObserver(Notificator.onSceneLeave, self.currentHintEnd_Scene)
        self.onItemPickedObserver = Notification.addObserver(Notificator.onItemPicked, self.currentHintEnd)
        self.onTipActivateWithoutParagraphsObserver = Notification.addObserver(Notificator.onTipRemoveWithoutParagraphs,
                                                                               self.currentHintEnd)
        self.onClickItemCollectHintSocketObserver = Notification.addObserver(Notificator.onClickItemCollectHintSocket,
                                                                             self.currentHintEnd)

        DialogBlockHint = DefaultManager.getDefaultBool("DialogBlockHint", True)
        if DialogBlockHint is True:
            self.onDialogOpenObserver = Notification.addObserver(Notificator.onDialogShow, self._onDialogOpen)
            self.onDialogCloseObserver = Notification.addObserver(Notificator.onDialogHide, self._onDialogClose)

    def _onDeactivate(self):
        if SystemManager.hasSystem("SystemHint") is False:
            return

        self.currentHintEnd()

        if TaskManager.existTaskChain("HintReadyEffect"):
            TaskManager.cancelTaskChain("HintReadyEffect")

        if TaskManager.existTaskChain("HintReloadEnter"):
            TaskManager.cancelTaskChain("HintReloadEnter")

        if TaskManager.existTaskChain("HintReady") is True:
            TaskManager.cancelTaskChain("HintReady")

        if TaskManager.existTaskChain("HintCharge") is True:
            TaskManager.cancelTaskChain("HintCharge")

        if TaskManager.existTaskChain("HintReloadStarted") is True:
            TaskManager.cancelTaskChain("HintReloadStarted")

        Notification.removeObserver(self.onSceneInitObserver)
        Notification.removeObserver(self.onQuestEndObserver)
        Notification.removeObserver(self.onCurrentHintEndObserver)
        # Notification.removeObserver(self.onInventorySlotsShiftObserver)
        Notification.removeObserver(self.onItemPlusLeaveObserver)
        Notification.removeObserver(self.onItemPickedObserver)
        Notification.removeObserver(self.onTipActivateWithoutParagraphsObserver)

        DialogBlockHint = DefaultManager.getDefaultBool("DialogBlockHint", True)
        if DialogBlockHint is True:
            Notification.removeObserver(self.onDialogOpenObserver)
            Notification.removeObserver(self.onDialogCloseObserver)

    # ---- TaskChains --------------------------------------------------------------------------------------------------

    def __tcHintReload(self):
        MovieGroup = self.getMovieGroup()

        if MovieGroup.hasObject("Movie2_Reload") is True:
            Movie_Reload = MovieGroup.getObject("Movie2_Reload")
            Movie_ReloadDuration = Movie_Reload.getDuration()

            SystemHint = SystemManager.getSystem("SystemHint")
            CurrentReloadTiming = SystemHint.getCurrentTiming()

            # Movie_Reload.setEnable(True)
            # with TaskManager.createTaskChain(Name="HintReloadEnter", Group=self.object,
            #                                  Repeat=True) as tc_hint_reload_enter:
            #     tc_hint_reload_enter.addTask("TaskMovie2SocketEnter", SocketName="socket", Movie2=Movie_Reload)
            #     tc_hint_reload_enter.addNotify(Notificator.onHintReloadEnter)
            # tc_hint_reload_enter.addTask("TaskMovie2SocketLeave", SocketName="socket", Movie2=Movie_Reload)
            # tc_hint_reload_enter.addNotify(Notificator.onHintReloadLeave)

            # Movie_Reload.setEnable(False)

            if Movie_ReloadDuration == CurrentReloadTiming or SystemHint.isReloadStarted() is False:
                # Movie_Reload.setEnable(True)
                # Movie_Reload.setLastFrame(True)

                with TaskManager.createTaskChain(Name="HintReadyEffect", Group=self.object) as tc:
                    tc.addTask(self.PolicyHintReady)

            if SystemHint.isReloadStarted() is True:
                with TaskManager.createTaskChain(Name="HintReloadStarted", Group=self.object) as tc:
                    tc.addTask("TaskStateChange", ID="StateHintReady", Value=False)

                    tc.addTask(self.PolicyHintReadyInterrupt)
                    tc.addTask(self.PolicyHintReload)
                    if MovieGroup.hasObject("Movie2_Charged") is True:
                        tc.addTask("PolicyHintCharged")
                    tc.addTask("TaskStateChange", ID="StateHintReady", Value=True)
                    tc.addTask(self.PolicyHintReady)

                    tc.addTask("TaskStateChange", ID="StateHintCharge", Value=False)
                    if MovieGroup.hasObject("Movie2_Reload") is False:
                        tc.addTask("TaskStateChange", ID="StateHintReady", Value=True)

    def __tcHintCharge(self):
        MovieGroup = self.getMovieGroup()

        with TaskManager.createTaskChain(Name="HintCharge", Group=self.object, Repeat=True) as tc:
            tc.addTask("TaskStateMutex", ID="StateHintCharge", From=True)
            tc.addTask(self.PolicyHintReload)

            if MovieGroup.hasObject("Movie2_Charged") is True:
                tc.addTask("PolicyHintCharged")

            tc.addTask("TaskStateChange", ID="StateHintReady", Value=True)
            tc.addTask(self.PolicyHintReady)
            tc.addTask("TaskStateChange", ID="StateHintCharge", Value=False)

            if MovieGroup.hasObject("Movie2_Reload") is False:
                tc.addTask("TaskStateChange", ID="StateHintReady", Value=True)

    def __tcHintReady(self):
        self.waitHintUIAction = DefaultManager.getDefaultBool("waitHintUIAction", False)
        self.waitNoReloadHintUIAction = DefaultManager.getDefaultBool("waitNoReloadHintUIAction", False)
        if self.waitHintUIAction is False and self.waitNoReloadHintUIAction is True:
            if _DEVELOPMENT is True:
                Trace.msg("<Hint> It seems that you set 'waitNoReloadHintUIAction' in Default.xlsx to True,"
                          "but 'waitHintUIAction'=False - it wouldn't work, you should enable 'waitHintUIAction' too!")

        with TaskManager.createTaskChain(Name="HintReady", Group=self.object, Repeat=True) as tc:
            tc.addScope(self.scopeClickHint)
            tc.addTask(self.PolicyHintPlay)

    # ---- Scopes ------------------------------------------------------------------------------------------------------

    def scopeHintLogic(self, source):
        def inHintPlay(state):
            self.inHintPlay = state

        source.addFunction(inHintPlay, True)

        source.addTask("TaskStateChange", ID="StateHintReady", Value=False)
        with source.addSwitchTask(4, self._hintPlay) as (tc_empty, tc_hint, tc_mind, tc_noReload):
            tc_empty.addNotify(Notificator.onHintClick, self.object, False, self.object.ACTION_EMPTY_USE)
            tc_empty.addTask(self.PolicyHintEmpty)
            tc_empty.addTask(self.PolicyHintReady)
            tc_empty.addTask("TaskStateChange", ID="StateHintReady", Value=True)

            tc_hint.addNotify(Notificator.onHintClick, self.object, True, self.object.ACTION_REGULAR_USE)
            tc_hint.addTask(self.PolicyHintReadyInterrupt)  # PolicyHintReadyMovieStop | stop and off Ready
            tc_hint.addTask(self.PolicyHintActivate)  # PolicyHintActivateMovie  | off Reload, play Activate
            tc_hint.addTask("TaskStateChange", ID="StateHintCharge", Value=True)
            tc_hint.addNotify(Notificator.onHintUIActionEnd)

            tc_mind.addNotify(Notificator.onHintClick, self.object, False, self.object.ACTION_MIND_USE)
            tc_mind.addTask("TaskPrint", Value="Hint not found active quest")
            tc_mind.addTask(self.PolicyHintNotFound)
            tc_mind.addTask(self.PolicyHintReady)
            tc_mind.addTask("TaskStateChange", ID="StateHintReady", Value=True)

            if self.waitNoReloadHintUIAction is False:  # show hint immediately
                tc_noReload.addNotify(Notificator.onHintUIActionEnd)
            with tc_noReload.addParallelTask(2) as (tc1, tc2):
                with tc1.addRaceTask(2) as (tc_hint_end, tc_delay):
                    tc_hint_end.addTask("TaskListener", ID=Notificator.onHintActionEnd)
                    tc_delay.addDelay(1000)
                tc2.addNotify(Notificator.onHintClick, self.object, False, self.object.ACTION_NO_RELOAD_USE)
                tc2.addTask(self.PolicyHintEmpty)
                tc2.addTask(self.PolicyHintReady)
            tc_noReload.addTask("TaskStateChange", ID="StateHintReady", Value=True)
            if self.waitNoReloadHintUIAction is True:  # wait for animation, then show hint
                tc_noReload.addNotify(Notificator.onHintUIActionEnd)

        source.addFunction(inHintPlay, False)

    def scopeClickHint(self, source):
        """ description: https://wonderland-games.atlassian.net/browse/HO2-661 """
        click_event = Event("HintRightClick")
        with source.addRepeatTask() as (repeat, until):
            with repeat.addRaceTask(2) as (click, reset):
                reset.addListener(Notificator.onStateChange,
                                  Filter=lambda id, state: id == "StateHintReady" and state is False)

                click.addTask("TaskStateMutex", ID="StateHintReady", From=True)
                click.addTask(self.PolicyHintClick)
                click.addFunction(click_event)

            until.addEvent(click_event)

    # ---- Observers ---------------------------------------------------------------------------------------------------

    def _onDialogOpen(self, dialogId):
        self.currentHintEnd()
        self.blockHint = True

        return False

    def _onDialogClose(self, dialogId, dialogObject):
        self.blockHint = False

        return False

    def _onSceneInit(self, sceneName):
        self.currentHintEnd()
        return False

    def _onQuestEnd(self, quest):
        if self.currentHint is None:
            return False

        currentQuest = self.currentHint.getQuest()

        if quest != currentQuest:
            return False

        self.currentHintEnd()
        return False

    def currentHintEnd_Scene(self, isSkip=None, next_Arg=None):
        if TaskManager.existTaskChain("HintAction_onEnd") is True:
            TaskManager.cancelTaskChain("HintAction_onEnd")
        self.currentHintEnd()
        return False

    def currentHintEnd(self, isSkip=None, next_Arg=None):
        # if TaskManager.existTaskChain("HintAction_onEnd") is True:
        #     TaskManager.cancelTaskChain("HintAction_onEnd")
        if self.currentHint is not None:
            self.currentHint.onEnd()
            self.currentHint = None

        if TaskManager.existTaskChain("HintPlay"):
            TaskManager.cancelTaskChain("HintPlay")
        return False

    # ---- Hint logic --------------------------------------------------------------------------------------------------

    def _hintPlay(self, isSkip, cb):
        if self.blockHint is True:
            self._debugHintLog("_hintPlay [cur={}] <0> BLOCK HINT")
            cb(isSkip, 0)
            return

        newHint = self.hintGive()
        self._debugHintLog("_hintPlay [cur={}] {}".format(self.currentHint, newHint))
        if self.currentHint is not None:
            if newHint.getQuest() is self.currentHint.getQuest() and self.currentHint.isEnd() is False:
                self._debugHintLog("_hintPlay [cur={}] <0> newHint.quest = curHint.quest ({}), curHint isEnd=False".format(
                    self.currentHint.__class__.__name__, newHint.getQuest()))
                cb(isSkip, 0)
                return

            self.currentHint.onEnd()

            self.currentHint = None
            if TaskManager.existTaskChain("HintPlay"):
                TaskManager.cancelTaskChain("HintPlay")

        currentSceneName = SceneManager.getCurrentSceneName()

        if SystemManager.hasSystem("SystemHintSceneExceptions") is True:
            GroupName = ZoomManager.getZoomOpenGroupName()
            if GroupName is None:
                GroupName = SceneManager.getSceneMainGroupName(currentSceneName)

            SystemHintSceneExceptions = SystemManager.getSystem("SystemHintSceneExceptions")
            hasException = SystemHintSceneExceptions.hasActiveException(currentSceneName, GroupName)
            if hasException is True:
                self._debugHintLog("_hintPlay [cur={}] <0> hasActiveException showMind ({}, {})".format(
                    self.currentHint, newHint.getQuest(), currentSceneName, GroupName))
                cb(isSkip, 0)
                SystemHintSceneExceptions.showMind(currentSceneName, GroupName)
                return

        self.currentHint = newHint
        if self.currentHint is not None:
            hintActionType = self.currentHint.getType()
            isValidateHint = HintManager.isValidateHint(hintActionType)
            if isValidateHint is True:
                self._debugHintLog("_hintPlay [cur={}] <1> quest={} valid - SHOW".format(
                    self.currentHint.__class__.__name__, newHint.getQuest(), hintActionType))
                cb(isSkip, 1)
                self.hintShow(self.currentHint)

                zoomOpenGroupName = ZoomManager.getZoomOpenGroupName()
                if zoomOpenGroupName is None:
                    return

                with TaskManager.createTaskChain(Name="HintPlay", Cb=self.currentHintEnd) as tc:
                    with tc.addRaceTask(2) as (tc_zoom, tc_scene):
                        tc_zoom.addTask("TaskZoomLeave", ZoomName=zoomOpenGroupName, SceneName=currentSceneName)
                        tc_scene.addTask("TaskSceneLeave", SceneName=currentSceneName)

            elif isValidateHint is False:
                self._debugHintLog("_hintPlay [cur={}] <3> quest={} invalid - SHOW".format(
                    self.currentHint.__class__.__name__, newHint.getQuest(), hintActionType))
                cb(isSkip, 3)
                self.hintShow(self.currentHint)
        else:
            self._debugHintLog("_hintPlay [cur={}] <2> none hint".format(self.currentHint))
            cb(isSkip, 2)

    def _debugHintLog(self, msg):
        if self.debug_hint_give is False:
            return
        Trace.msg("[Hint debug] {}".format(msg))

    def hintGive(self):
        self._debugHintLog("---- HintAction find [AroundSceneCheck={} ItemCollectCheck={} ZoomCheck={}] -----".format(
            self.AroundSceneCheck, self.ItemCollectCheck, self.ZoomCheck))

        HintAction = HintManager.findGlobalHint(self.object)
        if HintAction is not None:
            self._debugHintLog("[1] {} {}".format(HintAction.__class__.__name__, HintAction.Quest))
            return HintAction
        else:
            self._debugHintLog("[1] Not found global hint")

        currentSceneName = SceneManager.getCurrentSceneName()
        groupName = SceneManager.getSceneMainGroupName(currentSceneName)

        zoomGroupName = ZoomManager.getZoomOpenGroupName()
        if zoomGroupName is not None:
            """ Hint when Active zoom """

            HintAction = HintManager.findSceneHint(currentSceneName, zoomGroupName, self.object, True)

            if HintAction is not None:
                self._debugHintLog("[2] {} {}".format(HintAction.__class__.__name__, HintAction.Quest))
                return HintAction
            else:
                self._debugHintLog("[2] Not found scene hint [{} {} {}]".format(currentSceneName, zoomGroupName, True))

            if self.AroundSceneCheck is True:
                HintAction = self.getSceneHintAction(currentSceneName, groupName)

                if HintAction is not None:
                    HintAction = self.createZoomLeaveHintAction(currentSceneName, zoomGroupName)
                    self._debugHintLog("[3] AroundSceneCheck {}, created ZoomLeaveHintAction: {} {}".format(
                        currentSceneName, HintAction.__class__.__name__, HintAction.Quest))
                    return HintAction
                else:
                    self._debugHintLog("[3] (AroundSceneCheck) Not found scene hint [{} {}]".format(currentSceneName, groupName))

                HintSceneName, HintAction = self.getAroundSceneHintAction(currentSceneName, True)

                if HintAction is not None:
                    TransitionObject = TransitionManager.findTransitionObjectToScene(currentSceneName, HintSceneName)
                    if TransitionObject is not None:
                        if TransitionObject.getGroupName() == zoomGroupName:
                            HintAction = self.createSceneEnterHintAction(TransitionObject)
                            if HintAction is not None:
                                self._debugHintLog("[4] TransitionObject:{} == zoomGroupName:{} => {} {}".format(
                                    TransitionObject.getGroupName(), zoomGroupName, HintAction.__class__.__name__, HintAction.Quest))
                                return HintAction
                            else:
                                self._debugHintLog("[4] TransitionObject:{} == zoomGroupName:{} => scene enter hint NOT created".format(
                                    TransitionObject.getGroupName(), zoomGroupName))

                HintAction = self.createZoomLeaveHintAction(currentSceneName, zoomGroupName)
                self._debugHintLog("[5] AroundSceneCheck ZoomLeave, created ZoomLeaveHintAction: {} {}".format(
                    HintAction.__class__.__name__, HintAction.Quest))
                return HintAction

        else:
            """ Hint when No Active zoom """

            if EnigmaManager.getSceneActiveEnigma() is None:  # Enigmas with hint is more prioritized then item plus
                HintAction = self.getSpecialItemPlusHint(currentSceneName)
                if HintAction is not None:
                    self._debugHintLog("[6] SpecialItemPlus: {} {}".format(HintAction.__class__.__name__, HintAction.Quest))
                    return HintAction
                else:
                    self._debugHintLog("[6] SpecialItemPlus not found")

            HintAction = self.getSceneHintAction(currentSceneName, groupName)
            if HintAction is not None:
                self._debugHintLog("[7] {} {} [{} {}]".format(
                    HintAction.__class__.__name__, HintAction.Quest, currentSceneName, groupName))
                return HintAction
            else:
                self._debugHintLog("[7] getSceneHintAction not found [{} {}]".format(currentSceneName, groupName))

            if SceneManager.hasSpecialScene(currentSceneName) is True:
                HintAction = self.getSpecialSceneHintAction(currentSceneName, True)
                if HintAction is not None:
                    HintAction = self.createSpecialSceneEnterHintAction(currentSceneName)
                    if HintAction is not None:
                        self._debugHintLog("[8] createSpecialSceneEnterHintAction {} {}".format(
                            HintAction.__class__.__name__, HintAction.Quest))
                        return HintAction
                    else:
                        self._debugHintLog("[8] createSpecialSceneEnterHintAction not found [{}]".format(currentSceneName))

            if self.AroundSceneCheck is True:
                HintSceneName, HintActionAroundScene = self.getAroundSceneHintAction(currentSceneName, True)

                self._debugHintLog("-- AroundSceneCheck -- HintSceneName={}, HintActionAroundScene={}".format(
                    HintSceneName, HintActionAroundScene))

                if HintActionAroundScene is not None:
                    TransitionObject = TransitionManager.findTransitionObjectToScene(currentSceneName, HintSceneName)

                    if TransitionObject is not None:
                        if TransitionObject.active is False:
                            TransitionGroupName = TransitionObject.getGroupName()
                            HintAction = self.createZoomEnterHintAction(currentSceneName, TransitionGroupName, False)
                            if HintAction is not None:
                                self._debugHintLog("[9] AroundSceneCheck (TransitionObject is NOT active): {} {}".format(
                                    HintAction.__class__.__name__, HintAction.Quest))
                                return HintAction
                            else:
                                self._debugHintLog("[9] AroundSceneCheck (TransitionObject is NOT active): FAILED [{} {} {}]".format(
                                    currentSceneName, TransitionGroupName, False))
                        else:
                            HintAction = self.createSceneEnterHintAction(TransitionObject)
                            if HintAction is not None:
                                self._debugHintLog("[10] AroundSceneCheck (TransitionObject is ACTIVE): {} {}".format(
                                    HintAction.__class__.__name__, HintAction.Quest))
                                return HintAction
                            else:
                                self._debugHintLog("[10] AroundSceneCheck (TransitionObject is ACTIVE): FAILED [{}]".format(TransitionObject))

                    elif TransitionManager.hasTransitionBack(currentSceneName) is True:
                        TransitionBackObject = TransitionManager.getTransitionBackObject()
                        TransitionBackObjectScene = TransitionManager.getTransitionBack(currentSceneName)

                        if TransitionBackObjectScene == HintSceneName:
                            HintAction = self.createSceneEnterHintAction(TransitionBackObject)
                            if HintAction is not None:
                                self._debugHintLog("[11] AroundSceneCheck, hasTransitionBack {}: {} {}".format(
                                    currentSceneName, HintAction.__class__.__name__, HintAction.Quest))
                                return HintAction
                            else:
                                self._debugHintLog("[11] AroundSceneCheck, hasTransitionBack {}: FAILED [{}]".format(
                                    currentSceneName, TransitionBackObject))

            if SceneManager.isSpecialScene(currentSceneName) is True:
                HintAction = self.createSpecialSceneLeaveHintAction(currentSceneName)
                if HintAction is not None:
                    self._debugHintLog("[12] special scene {}: {} {}".format(
                        currentSceneName, HintAction.__class__.__name__, HintAction.Quest))
                    return HintAction
                else:
                    self._debugHintLog("[12] special scene {}: FAILED".format(currentSceneName))

    def getSpecialItemPlusHint(self, currentSceneName):
        if (SystemItemPlusScene.Open_Zoom is not None):
            hint = self.getSpecialItemPlusHint_SceneHint(currentSceneName)
        else:
            hint = self.getSpecialItemPlusHint_ClickOpen(currentSceneName)
        return hint

    def getSpecialItemPlusHint_SceneHint(self, currentSceneName):
        ScenePlus = SystemItemPlusScene.Open_Zoom[1]
        groupName = SceneManager.getSceneMainGroupName(ScenePlus)

        hasSceneActiveQuest = QuestManager.hasAroundSceneQuest(ScenePlus, groupName)
        if hasSceneActiveQuest is False:
            Sparks = DemonManager.getDemon("Sparks")
            param = Sparks.getParam("State")
            if param != "Ready":
                Notification.notify(Notificator.onItemZoomLeaveOpenZoom)
            else:
                return None

        HintAction = self.getSceneHintAction(ScenePlus, groupName, True)
        return HintAction

    def getSpecialItemPlusHint_ClickOpen(self, currentSceneName):
        Inventory = DemonManager.getDemon("Inventory")
        if (Inventory is None):
            return None

        if Inventory.isActive() is False:
            return None

        if SystemManager.hasSystem("SystemItemPlusScene") is False:
            return None

        SystemItemPlus = SystemManager.getSystem("SystemItemPlusScene")
        plus_Items = SystemItemPlus.items_Inventort

        for key, val in plus_Items.iteritems():
            ItemClick = val[0]
            ScenePlus = val[2].PlusScene
            groupName = SceneManager.getSceneMainGroupName(ScenePlus)
            hasSceneActiveQuest = QuestManager.hasAroundSceneQuest(ScenePlus, groupName)
            if (hasSceneActiveQuest is False):
                continue

            Inventory = DemonManager.getDemon("Inventory")
            if Inventory.hasInventoryItem(ItemClick) is False:
                continue
            if ItemClick.checkCount() is False:
                continue

            Params = dict(InventoryItem=ItemClick, Object=ItemClick)

            if QuestManager.hasLocalQuest(currentSceneName, groupName, "Click") is True:
                Quest = QuestManager.getSceneQuest(currentSceneName, groupName, "Click")
            else:
                Quest = QuestManager.createLocalQuest("Click", SceneName=ScenePlus, GroupName=groupName, Object=ItemClick)
                with TaskManager.createTaskChain() as tc:
                    with QuestManager.runQuest(tc, Quest) as tc_quest:
                        def fil(scene):
                            if (scene == ScenePlus):
                                return True
                            return False

                        tc_quest.addTask("TaskListener", ID=Notificator.onSceneEnter, Filter=fil)

            HintAction = HintManager.createHintAction("HintActionUseInventoryItem", Quest, **Params)
            return HintAction

    def getSpecialSceneHintAction(self, mainSceneName, checkActive=True):
        sceneName = SceneManager.getSpecialSceneName(mainSceneName)
        groupName = SceneManager.getSceneMainGroupName(sceneName)

        hasSceneActiveQuest = QuestManager.hasAroundSceneQuest(sceneName, groupName)
        if hasSceneActiveQuest is not False:
            hintAction = self.getSceneHintAction(sceneName, groupName, False)
            if hintAction is not None:
                if checkActive is True:
                    return hintAction

        zooms = SceneManager.getSceneZooms(sceneName)
        if zooms is None:
            return None

        for zoomGroupName in zooms:
            hintAction = HintManager.findSceneHint(sceneName, zoomGroupName, self.object, False)
            if hintAction is None:
                continue

            hintAction = self.createZoomEnterHintAction(sceneName, zoomGroupName, True)
            if hintAction is not None:
                return hintAction

    def createSpecialSceneEnterHintAction(self, SceneNameFrom):
        SceneNameTo = SceneManager.getSpecialSceneName(SceneNameFrom)
        if SceneNameTo is None:
            return None

        GroupNameFrom = SceneManager.getSceneMainGroupName(SceneNameFrom)
        # GroupNameTo = SceneManager.getSceneMainGroupName(SceneNameTo)
        SpecialEnterTrigger = DemonManager.getDemon("MagicVision")
        # DemonEntity = SpecialEnterTrigger.getEntity()
        # clickObject = DemonEntity.getSocket()
        # Params = dict(Demon = SpecialEnterTrigger, SceneNameTo = SceneNameTo)

        # if SceneNameTo in SpecialEnterTrigger.getBlockedScenes():
        #     return None

        if QuestManager.hasLocalQuest(SceneNameFrom, GroupNameFrom, "MagicVisionUse") is True:
            Quest = QuestManager.getSceneQuest(SceneNameFrom, GroupNameFrom, "MagicVisionUse")
        else:
            Quest = QuestManager.createLocalQuest("MagicVisionUse", SceneName=SceneNameFrom, GroupName=GroupNameFrom,
                                                  SceneNameTo=SceneNameTo, Demon=SpecialEnterTrigger)
            with TaskManager.createTaskChain() as tc:
                with QuestManager.runQuest(tc, Quest) as tc_quest:
                    tc_quest.addTask("TaskSceneLeave", SceneName=SceneNameFrom)

        HintAction = HintManager.createHintAction("HintActionMagicVisionUse", Quest)
        if HintAction._onCheck() is False:
            QuestManager.cancelQuest(Quest)
            return None

        return HintAction

    def createSpecialSceneLeaveHintAction(self, sceneNameFrom):
        SceneNameTo = SceneManager.getSpecialMainSceneName(sceneNameFrom)
        if SceneNameTo is None:
            return None

        GroupNameTo = SceneManager.getSceneMainGroupName(SceneNameTo)
        SpecialEnterTrigger = DemonManager.getDemon("MagicVision")
        DemonEntity = SpecialEnterTrigger.getEntity()
        clickObject = DemonEntity.getSocket()
        Params = dict(Object=clickObject)

        if QuestManager.hasLocalQuest(SceneNameTo, GroupNameTo, "Click") is True:
            Quest = QuestManager.getSceneQuest(SceneNameTo, GroupNameTo, "Click")
        else:
            Quest = QuestManager.createLocalQuest("Click", SceneName=SceneNameTo, GroupName=GroupNameTo, Object=clickObject)

            with TaskManager.createTaskChain() as tc:
                with QuestManager.runQuest(tc, Quest) as tc_quest:
                    tc_quest.addTask("TaskSceneLeave", SceneName=sceneNameFrom)

        HintAction = HintManager.createHintAction("HintActionClick", Quest, **Params)
        return HintAction

    def getSceneHintAction(self, sceneName, groupName, checkActive=True):
        hintAction = HintManager.findSceneHint(sceneName, groupName, self.object, checkActive)
        if hintAction is not None:
            self._debugHintLog("  getSceneHintAction {} :: {} {} {}".format(
                hintAction.__class__.__name__, sceneName, groupName, checkActive))
            return hintAction

        if self.ItemCollectCheck is True:
            hintAction = self.getItemCollectHintAction(sceneName)
            if hintAction is not None:
                return hintAction

        if self.ZoomCheck is True:
            hintAction = self.getZoomHintAction(sceneName)
            if hintAction is not None:
                self._debugHintLog("  getSceneHintAction ZoomCheck {} :: {} {} {}".format(
                    hintAction.__class__.__name__, sceneName, groupName, checkActive))
                return hintAction

        self._debugHintLog("  FAILED getSceneHintAction {} [{} {} {}]".format(hintAction, sceneName, groupName, checkActive))

    def getZoomHintAction(self, sceneName):
        if SceneManager.hasSceneZooms(sceneName) is False:
            return None

        zooms = SceneManager.getSceneZooms(sceneName)
        for zoomGroupName in zooms:
            hasSceneActiveQuest = QuestManager.hasAroundSceneQuest(sceneName, zoomGroupName)
            if hasSceneActiveQuest is False:
                continue

            hintAction = self.createZoomEnterHintAction(sceneName, zoomGroupName)
            if hintAction is None:
                continue
            return hintAction

    def getItemCollectHintAction(self, SceneName):
        itemCollects = SystemItemCollect.getItemList()
        for (ItemCollectSceneName, SocketName), (item_list, socket, flag) in itemCollects.iteritems():
            if SceneName != ItemCollectSceneName:
                continue
            if flag is True:
                continue
            Quest = QuestManager.createLocalQuest("ItemCollectOpen", SceneName=SceneName,
                                                  GroupName=SceneName, Object=socket)

            hintAction = HintManager.createHintAction("HintActionItemCollectOpen", Quest, SceneName=SceneName,
                                                      GroupName=SceneName, Object=socket)
            return hintAction

    def getAroundSceneHintAction(self, fromSceneName, checkActive=False):
        aroundScenes = TransitionManager.findSpiralScenes(fromSceneName)
        self._debugHintLog("* getAroundSceneHintAction from={} around={}".format(fromSceneName, aroundScenes))

        for sceneName in aroundScenes[1:]:
            groupName = SceneManager.getSceneMainGroupName(sceneName)
            hasSceneActiveQuest = QuestManager.hasAroundSceneQuest(sceneName, groupName)

            if hasSceneActiveQuest is True:
                hintAction = self.getSceneHintAction(sceneName, groupName, False)
                if hintAction is not None:
                    if checkActive is True:
                        TransitionObject = TransitionManager.findTransitionObjectToScene(fromSceneName, sceneName)
                        if TransitionObject is not None:
                            return sceneName, hintAction

            zooms = SceneManager.getSceneZooms(sceneName)
            if zooms is None:
                continue

            for zoomGroupName in zooms:
                hintAction = HintManager.findSceneHint(sceneName, zoomGroupName, self.object, False)
                if hintAction is None:
                    continue

                hintAction = self.createZoomEnterHintAction(sceneName, zoomGroupName, True)
                if hintAction is not None:
                    return sceneName, hintAction

            if SceneManager.hasSpecialScene(sceneName) is True:
                HintAction = self.getSpecialSceneHintAction(sceneName, checkActive)
                if HintAction is None:
                    return None, None

                HintAction = self.createSpecialSceneEnterHintAction(sceneName)
                if hintAction is not None:
                    return sceneName, HintAction
        return None, None

    def hintShow(self, HintAction):
        if self.waitHintUIAction is True and self.inHintPlay is True:
            tc_name = "HintShow_" + str(Mengine.getTimeMs())
            with TaskManager.createTaskChain(Name=tc_name) as tc:
                tc.addListener(Notificator.onHintUIActionEnd)
                tc.addFunction(HintAction.onAction, self)
        else:
            HintAction.onAction(self)

    def createZoomEnterHintAction(self, sceneName, zoomGroupName, check=True):
        zoom = ZoomManager.getZoom(zoomGroupName)

        if zoom.hasObject() is False:
            return None
        self._debugHintLog("createZoomEnterHintAction {} {} {}".format(sceneName, zoomGroupName, check))

        ZoomObject = ZoomManager.getZoomObject(zoomGroupName)
        if QuestManager.hasLocalQuest(sceneName, zoomGroupName, "EnterZoom") is True:
            Quest = QuestManager.getSceneQuest(sceneName, zoomGroupName, "EnterZoom")
        else:
            Quest = QuestManager.createLocalQuest("EnterZoom", Zoom=ZoomObject, GroupName=zoomGroupName, SceneName=sceneName)

        Params = dict(Zoom=ZoomObject)
        hintAction = HintManager.createHintAction("HintActionZoom", Quest, **Params)
        if hintAction.onCheck() is False:
            QuestManager.cancelQuest(Quest)
            self._debugHintLog("    createZoomEnterHintAction !!! {} onCheck false - cancel quest".format(hintAction.__class__.__name__))
            return None

        if QuestManager.hasLocalQuest(sceneName, zoomGroupName, "EnterZoom") is False:
            currentSceneName = SceneManager.getCurrentSceneName()

            with TaskManager.createTaskChain() as tc:
                with QuestManager.runQuest(tc, Quest) as tc_quest:
                    with tc_quest.addRaceTask(2) as (tc_zoom, tc_scene):
                        tc_zoom.addTask("TaskZoomEnter", ZoomName=zoomGroupName, SceneName=sceneName)
                        tc_scene.addTask("TaskSceneLeave", SceneName=currentSceneName)

        if check is False:
            self._debugHintLog("    createZoomEnterHintAction :) {} check false - return hintAction".format(hintAction.__class__.__name__))
            return hintAction

        hasZoomActiveQuest = QuestManager.hasAroundSceneQuest(sceneName, zoomGroupName)
        if hasZoomActiveQuest is False:
            self._debugHintLog("    createZoomEnterHintAction !!! {} hasZoomActiveQuest false".format(hintAction.__class__.__name__))
            return None

        groupName = zoomGroupName
        hintAction = self.getSceneHintAction(sceneName, groupName, False)
        if hintAction is None:
            self._debugHintLog("    createZoomEnterHintAction !!! hintAction is None")
            return None

        return hintAction

    def createZoomLeaveHintAction(self, currentSceneName, zoomGroupName):
        Quest = QuestManager.createLocalQuest("CloseZoom", GroupName=zoomGroupName, SceneName=currentSceneName)

        with TaskManager.createTaskChain() as tc:
            with QuestManager.runQuest(tc, Quest) as tc_quest:
                with tc_quest.addRaceTask(3) as (tc_zoom, tc_scene, tc_hint):
                    tc_zoom.addTask("TaskZoomLeave", ZoomName=zoomGroupName, SceneName=currentSceneName)
                    tc_scene.addTask("TaskSceneLeave", SceneName=currentSceneName)
                    tc_hint.addTask(self.PolicyHintClick)

        HintAction = HintManager.createHintAction("HintActionZoomOut", Quest)
        return HintAction

    def createSceneEnterHintAction(self, TransitionObject):
        if TransitionObject is None:
            return None

        currentSceneName = SceneManager.getCurrentSceneName()

        Params = dict(Transition=TransitionObject)
        SceneNameTo = TransitionManager.getTransitionSceneTo(TransitionObject)
        GroupNameTo = SceneManager.getSceneMainGroupName(SceneNameTo)

        if SceneNameTo is None:
            return None

        if QuestManager.hasLocalQuest(SceneNameTo, GroupNameTo, "EnterScene") is True:
            Quest = QuestManager.getSceneQuest(SceneNameTo, GroupNameTo, "EnterScene")
        else:
            Quest = QuestManager.createLocalQuest("EnterScene", SceneName=SceneNameTo,
                                                  GroupName=GroupNameTo, Transition=TransitionObject)

            with TaskManager.createTaskChain() as tc:
                with QuestManager.runQuest(tc, Quest) as tc_quest:
                    tc_quest.addTask("TaskSceneLeave", SceneName=currentSceneName)

        if TransitionObject.getName() in ["Transition_Back", "Movie2Button_NavGoBack"]:
            if Mengine.hasTouchpad() is True:
                HintAction = HintManager.createHintAction("HintActionTransitionBackMobile", Quest, **Params)
            else:
                HintAction = HintManager.createHintAction("HintActionTransitionBack", Quest, **Params)

            if HintAction.onCheck():
                return HintAction

        HintAction = HintManager.createHintAction("HintActionTransition", Quest, **Params)

        if HintAction.onCheck():
            return HintAction
