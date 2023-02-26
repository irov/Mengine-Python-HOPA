import Trace
from Foundation.GroupManager import GroupManager
from Foundation.Initializer import Initializer
from Foundation.Params import Params
from Foundation.SceneManager import SceneManager
from Foundation.SystemManager import SystemManager
from Foundation.Task.MixinScene import MixinScene
from HOPA.HintManager import HintManager
from HOPA.ZoomManager import ZoomManager
from Notification import Notification

class HintAction(MixinScene, Params, Initializer):
    def __init__(self):
        super(HintAction, self).__init__()

        self.Quest = None

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

    def appendInterruptCb(self, isSkip, __complete_cb, policy):
        if isSkip is False:
            self.appendInterrupt(policy)
        else:
            pass

        __complete_cb(False)

    def removeInterruptCb(self, isSkip, __complete_cb, policy):
        if isSkip is False:
            self.removeInterrupt(policy)
        else:
            pass

        __complete_cb(False)

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

    def _onInitializeFailed(self, msg):
        Trace.log("HintAction", 0, "HintAction %s:%s initialize failed: %s" % (self.actionType, self.Quest.getType(), msg))
        pass

    def _onFinalizeFailed(self, msg):
        Trace.log("HintAction", 0, "HintAction %s:%s finalize failed: %s" % (self.actionType, self.Quest.getType(), msg))
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
        print(self.__class__.__name__)
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

    def onAction(self, hint):
        Notification.notify(Notificator.onHintActionStart, self)
        self._onAction(hint)
        pass

    def _onAction(self, hint):
        pass

    def onEnd(self):
        self._onEnd()
        pass

    def _onEnd(self):
        pass

    pass