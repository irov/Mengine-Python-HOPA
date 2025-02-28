from Foundation.DefaultManager import DefaultManager
from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.SceneManager import SceneManager
from Foundation.TaskManager import TaskManager
from HOPA.QuestIconManager import QuestIconManager
from HOPA.QuestManager import QuestManager
from HOPA.TransitionManager import TransitionManager
from HOPA.ZoomManager import ZoomManager
from Notification import Notification


class QuestIcon(BaseEntity):
    def __init__(self):
        super(QuestIcon, self).__init__()
        if Mengine.hasTouchpad() is False:
            return
        self.questFilter = QuestIconManager.getQuests()
        self.questIconActions = {}
        self.sceneZoomQuests = {}
        self.sceneTransitionQuests = {}
        self.activeQuests = []
        pass

    def _onActivate(self):
        if Mengine.hasTouchpad() is False:
            return

        self.onZoomEnter = Notification.addObserver(Notificator.onZoomEnter, self._onZoomEnter)
        self.onSceneEnter = Notification.addObserver(Notificator.onSceneEnter, self._onSceneEnter)
        self.onZoomLeave = Notification.addObserver(Notificator.onZoomLeave, self._onZoomLeave)
        self.onQuestRun = Notification.addObserver(Notificator.onQuestRun, self._onQuestRun)
        self.onQuestEnd = Notification.addObserver(Notificator.onQuestEnd, self._onQuestEnd)

        self.onTransitionBlockOpenObserver = Notification.addObserver(Notificator.onTransitionBlockOpen, self._onTransitionBlockOpen)

        self.enableGlobalMouseEvent(True)
        self._delayQuestIconShow()

        self._loadIcons(True)
        self._questIconShow()
        pass

    def _onSceneEnter(self, sceneName):
        transitions = TransitionManager.getOpenSceneTransitions(sceneName)
        for TransitionObject in transitions:
            SceneNameTo = TransitionManager.getTransitionSceneTo(TransitionObject)
            if SceneNameTo is None:
                continue

            if TaskManager.existTaskChain("Open%s" % (SceneNameTo)):
                continue
            GroupNameTo = SceneManager.getSceneMainGroupName(SceneNameTo)
            Quest = QuestManager.createLocalQuest("EnterScene", SceneName=SceneNameTo,
                                                  GroupName=GroupNameTo, Transition=TransitionObject)

            with TaskManager.createTaskChain(Name="Open%s" % (SceneNameTo)) as tc:
                with QuestManager.runQuest(tc, Quest) as tc_quest:
                    tc_quest.addTask("TaskSceneEnter", SceneName=SceneNameTo)
                    pass
                pass

            self._addIconNode(Quest)
            self.sceneTransitionQuests[SceneNameTo] = Quest
            pass

        self._questIconShow()
        return False

    def _onTransitionBlockOpen(self, object, value):
        if value is True:
            return False
            pass

        enable = object.getParam("Enable")
        if enable is False:
            return False
            pass

        blockOpen = object.getParam("BlockOpen")
        if blockOpen is True:
            return False
            pass

        SceneNameTo = TransitionManager.getTransitionSceneTo(object)
        if SceneNameTo is None:
            return False
            pass

        if TaskManager.existTaskChain("Open%s" % (SceneNameTo)):
            return False
            pass
        GroupNameTo = SceneManager.getSceneMainGroupName(SceneNameTo)
        Quest = QuestManager.createLocalQuest("EnterScene", SceneName=SceneNameTo,
                                              GroupName=GroupNameTo, Transition=object)

        with TaskManager.createTaskChain(Name="Open%s" % (SceneNameTo)) as tc:
            with QuestManager.runQuest(tc, Quest) as tc_quest:
                tc_quest.addTask("TaskSceneEnter", SceneName=SceneNameTo)
                pass
            pass

        self._addIconNode(Quest)
        self.sceneTransitionQuests[SceneNameTo] = Quest
        self._questIconShow()
        return False
        pass

    def _delayQuestIconShow(self):
        with TaskManager.createTaskChain(Name="DelayQuestIconShow", Repeat=True) as tc:
            with tc.addRaceTask(2) as (tc_delay, tc_click):
                tc_delay.addFunction(self._loadIcons, True)
                tc_delay.addFunction(self._questIconShow)

                QuestIconDefaultTime = DefaultManager.getDefaultFloat("QuestIconDefaultTime", 10)
                QuestIconDefaultTime *= 1000  # speed fix
                tc_delay.addDelay(QuestIconDefaultTime)

                tc_delay.addFunction(self._loadIcons, False)
                tc_delay.addFunction(self._questIconShow)

                tc_click.addTask("TaskMouseButtonClick", isDown=True)
                tc_click.addFunction(self._questIconHide)
                pass

            pass
        pass

    def _questIconShow(self):
        for QuestIconAction in self.questIconActions.values():
            if QuestIconAction.onCheck() is False:
                continue
                pass

            obj = QuestIconAction.getQuestIconObject()
            if obj in self.activeQuests:
                continue
                pass

            self.activeQuests.append(obj)

            QuestIconAction.onAction()
            pass
        pass

    def _questIconHide(self):
        for QuestIconAction in self.questIconActions.values():
            if QuestIconAction.isActiveIcon() is False:
                continue
                pass
            obj = QuestIconAction.getQuestIconObject()

            QuestIconAction.onEnd()

            if obj not in self.activeQuests:
                continue
                pass

            self.activeQuests.remove(obj)
            pass
        pass

    def _loadIcons(self, start):
        sceneName = SceneManager.getCurrentSceneName()
        groupName = SceneManager.getSceneMainGroupName(sceneName)

        zooms = ZoomManager.getActiveSceneZooms(sceneName)
        transitions = TransitionManager.getOpenSceneTransitions(sceneName)

        for zoom in zooms:
            ZoomObject = zoom.getObject()
            ZoomGroupName = ZoomManager.getZoomGroupName(ZoomObject)

            if TaskManager.existTaskChain("Open%s" % (ZoomObject.getName())):
                continue
                pass

            Quest = QuestManager.createLocalQuest("EnterZoom", Zoom=ZoomObject,
                                                  SceneName=sceneName, GroupName=ZoomGroupName)

            with TaskManager.createTaskChain(Name="Open%s" % (ZoomObject.getName())) as tc:
                with QuestManager.runQuest(tc, Quest) as tc_quest:
                    tc_quest.addTask("TaskZoomInit", ZoomName=ZoomGroupName, SceneName=sceneName)
                    pass
                pass

            self._addIconNode(Quest)
            self.sceneZoomQuests[ZoomObject] = Quest
            pass

        for TransitionObject in transitions:
            SceneNameTo = TransitionManager.getTransitionSceneTo(TransitionObject)
            if SceneNameTo is None:
                continue

            if TaskManager.existTaskChain("Open%s" % (SceneNameTo)):
                continue

            GroupNameTo = SceneManager.getSceneMainGroupName(SceneNameTo)
            Quest = QuestManager.createLocalQuest("EnterScene", SceneName=SceneNameTo,
                                                  GroupName=GroupNameTo, Transition=TransitionObject)

            with TaskManager.createTaskChain(Name="Open%s" % (SceneNameTo)) as tc:
                with QuestManager.runQuest(tc, Quest) as tc_quest:
                    tc_quest.addTask("TaskSceneEnter", SceneName=SceneNameTo)
                    pass
                pass

            self._addIconNode(Quest)
            self.sceneTransitionQuests[SceneNameTo] = Quest
            pass
        pass

        activeQuestsCache = QuestManager.getSceneQuests(sceneName, groupName)

        if activeQuestsCache is None:
            return False

        for quest in activeQuestsCache:
            questType = quest.questType
            if questType not in self.questFilter.keys():
                continue
                pass
            questIconActionName, spriteIconName, useQuestObject, startEnable = self.questFilter[questType]

            #            print "startEnable, start = ",startEnable, start, questIconActionName
            if startEnable != start:
                continue
                pass

            if useQuestObject is False:
                continue
                pass
            if len(quest.params) == 0:
                continue
                pass
            if quest in self.questIconActions:
                continue

            self._addIconNode(quest)
            pass

        return False
        pass

    def _addIconNode(self, quest):
        if quest is None:
            return

        questType = quest.questType
        if questType not in self.questFilter.keys():
            return
            pass

        if quest.active is False:
            return
            pass

        if quest.isComplete() is True:
            return
            pass

        iconObj = QuestIconManager.getQuestIcon(questType)

        QuestIconActionClass = QuestIconManager.getQuestIconAction(questType)
        if QuestIconActionClass is None:
            Trace.log("Entity", 0, "QuestIcon _addIconNode: QuestIconActionClass is None")
            return

        QuestIconAction = QuestIconActionClass()

        copyParams = {}
        for param, value in quest.params.iteritems():
            copyParams[param] = value
            pass

        QuestIconAction.onParams(copyParams)
        QuestIconAction.setQuest(quest)
        QuestIconAction.setParentQuestIconObject(iconObj)
        QuestIconAction.onInitialize()

        self.questIconActions[quest] = QuestIconAction
        pass

    def _onZoomEnter(self, zoomGroupName):
        return False

    def _onZoomLeave(self, zoomGroupName):
        return False

    def _onQuestRun(self, quest):
        questType = quest.questType
        if questType not in self.questFilter.keys():
            return False
            pass

        if quest.active is False:
            return
            pass

        if quest.isComplete() is True:
            return
            pass

        questIconActionName, spriteIcon, useQuestObject, startEnable = self.questFilter[questType]

        if useQuestObject is False:
            return False

        questSceneName = quest.params.get("SceneName")
        currentSceneName = SceneManager.getCurrentSceneName()
        if questSceneName != currentSceneName:
            return False

        self._addIconNode(quest)
        if startEnable is True:
            self._questIconShow()
            pass
        return False

    def _onQuestEnd(self, quest):
        if quest not in self.questIconActions.keys():
            return False

        QuestIconAction = self.questIconActions[quest]
        obj = QuestIconAction.getQuestIconObject()
        QuestIconAction.onEnd()
        del self.questIconActions[quest]
        if obj in self.activeQuests:
            self.activeQuests.remove(obj)
            pass

        if quest in self.sceneZoomQuests.keys():
            del self.sceneZoomQuests[quest]
            pass

        if quest in self.sceneTransitionQuests.keys():
            del self.sceneTransitionQuests[quest]
            pass

        return False
        pass

    def _onDeactivate(self):
        if Mengine.hasTouchpad() is False:
            return
        Notification.removeObserver(self.onZoomEnter)
        Notification.removeObserver(self.onSceneEnter)
        Notification.removeObserver(self.onZoomLeave)
        Notification.removeObserver(self.onQuestRun)
        Notification.removeObserver(self.onQuestEnd)
        Notification.removeObserver(self.onTransitionBlockOpenObserver)

        for zoomObject, quest in self.sceneZoomQuests.iteritems():
            if quest not in self.questIconActions:
                continue
            QuestIconAction = self.questIconActions[quest]
            QuestIconAction.onEnd()
            QuestManager.cancelQuest(quest)
            del self.questIconActions[quest]
            if TaskManager.existTaskChain("Open%s" % (zoomObject.name)):
                TaskManager.cancelTaskChain("Open%s" % (zoomObject.name))
            pass

        self.sceneZoomQuests = {}
        self.activeQuests = []

        for sceneNameTo, quest in self.sceneTransitionQuests.iteritems():
            if quest not in self.questIconActions:
                continue
            QuestIconAction = self.questIconActions[quest]
            QuestIconAction.onEnd()
            QuestManager.cancelQuest(quest)
            del self.questIconActions[quest]
            if TaskManager.existTaskChain("Open%s" % (sceneNameTo)):
                TaskManager.cancelTaskChain("Open%s" % (sceneNameTo))
            pass

        self.sceneTransitionQuests = {}

        for QuestIconAction in self.questIconActions.values():
            QuestIconAction.onEnd()
            pass

        self.questIconActions = {}
        self.enableGlobalMouseEvent(False)

        if TaskManager.existTaskChain("DelayQuestIconShow"):
            TaskManager.cancelTaskChain("DelayQuestIconShow")
            pass
        pass

    pass
