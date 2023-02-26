import Trace
from Foundation.Initializer import Initializer
from Foundation.Params import Params
from Foundation.Task.MixinScene import MixinScene
from HOPA.CruiseControlManager import CruiseControlManager

class CruiseAction(MixinScene, Params, Initializer):
    def __init__(self):
        super(CruiseAction, self).__init__()
        self.Quest = None

        self.actionType = ''

        self.listInterrupt = []

    def appendInterrupt(self, name):
        self.listInterrupt.append(name)

    def listInterruptClean(self, isSkip):
        self.listInterrupt = []

    def removeInterrupt(self, name):
        if name not in self.listInterrupt:
            return
        self.listInterrupt.remove(name)

    def setQuest(self, Quest):
        self.Quest = Quest

    def getQuest(self):
        return self.Quest

    def setType(self, actionType):
        self.actionType = actionType

    def getType(self):
        return self.actionType

    def _onInitializeFailed(self, msg):
        Trace.log("CruiseAction", 0, "CruiseAction %s:%s initialize failed: %s" % (self.actionType, self.Quest, msg))
        pass

    def _onFinalizeFailed(self, msg):
        Trace.log("CruiseAction", 0, "CruiseAction %s:%s finalize failed: %s" % (self.actionType, self.Quest, msg))
        pass

    def getCruiseObject(self):
        return self._getCruiseObject()

    def _getCruiseObject(self):
        return

    def onCheck(self):
        object_ = self.getCruiseObject()

        if object_ is None:
            return self._onCheck()

        if CruiseControlManager.inBlackList(object_) is True:
            return False

        Enable = object_.getEnable()

        if Enable is False:
            return False

        BlockInteractive = object_.getParam("BlockInteractive")
        if BlockInteractive is True:
            return False

        return self._onCheck()

    def _onCheck(self):
        return True

    def onAction(self):
        self._onAction()

    def _onAction(self):
        return

    def onEnd(self):
        self._onEnd()

    def _onEnd(self):
        return