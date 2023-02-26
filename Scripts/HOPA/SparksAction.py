from Foundation.Initializer import Initializer
from Foundation.Params import Params
from Foundation.Task.MixinScene import MixinScene
from HOPA.SparksManager import SparksManager

class SparksAction(MixinScene, Params, Initializer):
    def __init__(self):
        super(SparksAction, self).__init__()

        self.ID = None
        self.sparksObject = None
        pass

    def setID(self, ID):
        self.ID = ID
        pass

    def getID(self):
        return self.ID
        pass

    def setType(self, actionType):
        self.actionType = actionType
        pass

    def getType(self):
        return self.actionType
        pass

    def getEffectObject(self):
        effectObject = SparksManager.getActionEffect(self.actionType)

        return effectObject
        pass

    def _onParams(self, params):
        super(SparksAction, self)._onParams(params)
        pass

    def _onInitialize(self):
        super(SparksAction, self)._onInitialize()
        pass

    def _onInitializeFailed(self, msg):
        Trace.log("SparksAction", 0, "SparksAction %s:%s initialize failed: %s" % (self.actionType, self.ID, msg))
        pass

    def _onFinalizeFailed(self, msg):
        Trace.log("SparksAction", 0, "SparksAction %s:%s finalize failed: %s" % (self.actionType, self.ID, msg))
        pass

    def onCheck(self):
        obj = self._getSparksObject()

        if obj is None:
            return self._onCheck()
            pass

        if obj.getEnable() is False:
            return False
            pass

        if obj.isInteractive() is False:
            return False
            pass

        if obj.isActive() is False:
            return False
            pass

        return self._onCheck()
        pass

    def _getSparksObject(self):
        return None
        pass

    def _onCheck(self):
        return True
        pass

    def onAction(self):
        self._onAction()
        pass

    def _onAction(self, hint, cb):
        pass

    def onEnd(self):
        self._onEnd()
        pass

    def _onEnd(self):
        pass
    pass