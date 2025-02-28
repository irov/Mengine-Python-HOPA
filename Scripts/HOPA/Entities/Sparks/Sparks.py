from Foundation.DefaultManager import DefaultManager
from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.Notificator import Notificator
from Foundation.SceneManager import SceneManager
from Foundation.SystemManager import SystemManager
from Foundation.TaskManager import TaskManager
from HOPA.HintManager import HintManager
from HOPA.SparksManager import SparksManager
from HOPA.ZoomManager import ZoomManager
from Notification import Notification


class Sparks(BaseEntity):
    @staticmethod
    def declareORM(Type):
        BaseEntity.declareORM(Type)
        Type.addAction(Type, "State")

    def __init__(self):
        super(Sparks, self).__init__()
        self.currentAction = None

    def _onActivate(self):
        self.onZoomInit = Notification.addObserver(Notificator.onZoomInit, self._Sparks_End)
        self.onZoomLeave = Notification.addObserver(Notificator.onZoomLeave, self._Sparks_End)
        with TaskManager.createTaskChain(Name="SparksReady", Repeat=True) as tc:
            SparksDelayTime = DefaultManager.getDefaultFloat("SparksDelayTime", 2)
            SparksDelayTime *= 1000.0  # speed fix
            tc.addDelay(SparksDelayTime)

            # tc.addTask("TaskFunction", Fn = self._sparksGive)

            tc.addFunction(self._sparksHint)

    def _onDeactivate(self):
        Notification.removeObserver(self.onZoomInit)
        Notification.removeObserver(self.onZoomLeave)

        if TaskManager.existTaskChain("SparksReady") is True:
            TaskManager.cancelTaskChain("SparksReady")

        self._Sparks_End()

        self.currentAction = None

    def _sparksGive(self):
        self._Sparks_End()

        currentSceneName = SceneManager.getCurrentSceneName()
        if currentSceneName is None:
            return

        groupName = ZoomManager.getZoomOpenGroupName()
        if groupName is None:
            groupName = SceneManager.getSceneMainGroupName(currentSceneName)

        SparksAction = SparksManager.findSceneSparksAction(currentSceneName, groupName)
        if SparksAction is None:
            return

        SparksAction.onAction()
        self.currentAction = SparksAction

    def _sparksHint(self):
        if Mengine.getCurrentAccountSettingBool("DifficultyCustomSparklesOnActiveAreas") is False:
            return

        if self.currentAction is not None:
            self.currentAction.onEnd()

        if SparksManager.hasSparksAction("SparksActionHint") is False:
            return

        self.object.setParam("State", "Ready")
        sceneName = SceneManager.getCurrentSceneName()
        groupName = ZoomManager.getZoomOpenGroupName()

        if sceneName is None:
            return

        SystemHint = SystemManager.getSystem("SystemHint")
        DemonHint = SystemHint.getHintObject()
        Entity = DemonHint.getEntity()

        if groupName is None:
            groupName = SceneManager.getSceneMainGroupName(sceneName)

        hintAction = HintManager.findSceneHint(sceneName, groupName, DemonHint, True)
        if hintAction is None:
            hintAction = HintManager.findGlobalHint(DemonHint)

            if hintAction is None:
                if SystemManager.hasSystem("SystemHint") is False:
                    return

                hintAction = Entity.hintGive()
                if hintAction is None:
                    return

        hintActionObj = hintAction.getHintObject()
        if hintActionObj is None:
            return

        params = dict(Zoom=hintActionObj)

        SparksAction = SparksManager.createSparksAction("SparksActionHint", **params)
        SparksAction.onAction()
        self.currentAction = SparksAction

    def _Sparks_End(self, *_):
        if self.currentAction is not None:
            self.currentAction.onEnd()
            self.currentAction = None
        return False
