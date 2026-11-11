from Foundation.GroupManager import GroupManager
from Foundation.Initializer import Initializer
from Foundation.Params import Params
from Foundation.SceneManager import SceneManager
from Foundation.SystemManager import SystemManager
from Foundation.Task.MixinScene import MixinScene
from Foundation.TaskManager import TaskManager
from HOPA.HintManager import HintManager
from HOPA.ZoomManager import ZoomManager


class HintAction(MixinScene, Params, Initializer):
    def __init__(self):
        super(HintAction, self).__init__()

        self.Quest = None
        self._task_chain = None
        self._scroll_chain = None
        self._end_chain = None

        self.listInterrupt = []
        self.endAction = False
        self.onClickItemCollectHint = None
        pass

    def setEnd(self):
        self.endAction = True

        Notification.notify(Notificator.onHintActionEnd, self)
        pass

    def isEnd(self):
        return self.endAction
        pass

    def getStart_Position(self):
        SystemHint = SystemManager.getSystem("SystemHint")
        Hint = SystemHint.getHintObject()
        P0 = Hint.getPoint()
        return P0

    def appendInterruptCb(self, isSkip, cb, policy):
        if isSkip is False:
            self.appendInterrupt(policy)
        else:
            pass

        cb(False)

    def removeInterruptCb(self, isSkip, cb, policy):
        if isSkip is False:
            self.removeInterrupt(policy)
        else:
            pass

        cb(False)

    def appendInterrupt(self, name):
        self.listInterrupt.append(name)
        pass

    def listInterruptClean(self, isSkip):
        self.listInterrupt = []
        pass

    def removeInterrupt(self, name):
        if name not in self.listInterrupt:
            return
        self.listInterrupt.remove(name)
        pass

    def setQuest(self, Quest):
        self.Quest = Quest
        pass

    def getQuest(self):
        return self.Quest
        pass

    def setType(self, actionType):
        self.actionType = actionType
        pass

    def getType(self):
        return self.actionType
        pass

    def _onInitializeFailed(self, ex):
        Trace.log_exception("HintAction", 0, "HintAction %s:%s initialize failed: %s" % (self.actionType, self.Quest.getType(), ex))
        pass

    def _onFinalizeFailed(self, ex):
        Trace.log_exception("HintAction", 0, "HintAction %s:%s finalize failed: %s" % (self.actionType, self.Quest.getType(), ex))
        pass

    def getHintObject(self):
        return self._getHintObject()
        pass

    def getHintTargetPosition(self, Hint):
        return (0, 0)
        pass

    def getHintPosition(self, Object):
        return self._getHintPosition(Object)
        pass

    def _getHintPosition(self, Object):
        return None

    def getHintDoublePosition(self, Object):
        return self._getHintDoublePosition(Object)

    def _getHintDoublePosition(self, Object):
        return None

    def _getHintObject(self):
        return None
        pass

    def getFollow_Node(self):
        return None

    def Create_Movie(self, name):
        layer = self.getHintLayer()

        Group = GroupManager.getGroup("HintEffect")
        if Group.hasObject(name):
            return None

        Movie = Group.generateObject(name, name)
        node = Movie.getEntityNode()
        layer.addChild(node)
        Movie.setEnable(True)
        return Movie

    def getHintLayer(self):
        scene = SceneManager.getCurrentScene()
        if Mengine.hasTouchpad() is True and ZoomManager.getZoomOpenGroupName() is None:
            layer = scene.getMainLayer()
        else:
            layer = scene.getSlot("HintEffect")
        return layer

    def destroy_movie(self, name):
        Group = GroupManager.getGroup("HintEffect")
        if Group.hasObject(name):
            movie = Group.getObject(name)
            movie.onDestroy()
        else:
            pass

        return None

    def destroy_own_movie(self, name, movie):
        # Hint movies share fixed names in the "HintEffect" group, so a probe or a replaced
        # hint action must not destroy the movies that belong to the hint being shown now.
        if movie is None:
            return None

        Group = GroupManager.getGroup("HintEffect")
        if Group.hasObject(name) is False:
            return None

        if Group.getObject(name) is not movie:
            return None

        movie.onDestroy()

        return None

    def onCheck(self):
        object = self.getHintObject()
        if object is None:
            return self._onCheck()
            pass

        if HintManager.inBlackList(object) is True:
            return False
            pass

        Enable = object.getEnable()

        if Enable is False:
            return False
            pass

        BlockInteractive = object.getParam("BlockInteractive")
        if BlockInteractive is True:
            return False
            pass
        return self._onCheck()
        pass

    def _onCheck(self):
        return True
        pass

    def _onFinalize(self):
        super(HintAction, self)._onFinalize()

        self._clearScrollChain()
        self._clearTaskChain()
        self.cancelEndEffect()
        self.Quest = None
        self.listInterrupt = []
        self.onClickItemCollectHint = None

    def _clearTaskChain(self):
        task_chain = self._task_chain
        self._task_chain = None
        if task_chain is not None:
            task_chain.cancel()

    def _clearScrollChain(self):
        scroll_chain = self._scroll_chain
        self._scroll_chain = None
        if scroll_chain is not None:
            scroll_chain.cancel()

    def _runScrolling(self, hint):
        self._scroll_chain = TaskManager.createTaskChain(Cb=self._onScrollComplete, CbArgs=(hint,))
        with self._scroll_chain as source:
            source.addScope(self._onScroll)

    def _onScroll(self, source):
        pass

    def _onScrollComplete(self, isSkip, hint):
        self._scroll_chain = None
        self._runAction(hint)

    def cancelEndEffect(self):
        end_chain = self._end_chain
        self._end_chain = None
        if end_chain is not None:
            end_chain.cancel()

    def _runEndEffect(self):
        self.cancelEndEffect()

        self._end_chain = TaskManager.createTaskChain(Cb=self._onEndEffectComplete)
        with self._end_chain as source:
            source.addScope(self._onEndEffect)

    def _onEndEffect(self, source):
        pass

    def _onEndEffectComplete(self, isSkip):
        self._end_chain = None

    def onAction(self, hint):
        Notification.notify(Notificator.onHintActionStart, self)

        self._clearScrollChain()
        self._clearTaskChain()
        self.cancelEndEffect()
        self._onActionStart(hint)

    def _onActionStart(self, hint):
        self._runAction(hint)

    def _runAction(self, hint):
        self._task_chain = TaskManager.createTaskChain(Cb=self._onActionComplete)
        with self._task_chain as source:
            source.addScope(self._onAction, hint)

    def _onActionComplete(self, isSkip):
        self._task_chain = None

    def _onAction(self, source, hint):
        pass

    def onEnd(self):
        self._clearScrollChain()
        self._onEnd()
        pass

    def _onEnd(self):
        self._clearTaskChain()
