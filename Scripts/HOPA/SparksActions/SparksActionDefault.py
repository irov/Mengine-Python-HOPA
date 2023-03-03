from Foundation import Utils
from Foundation.ArrowManager import ArrowManager
from Foundation.DemonManager import DemonManager
from Foundation.SceneManager import SceneManager
from Foundation.Task.MixinGroup import MixinGroup
from HOPA.SparksAction import SparksAction
from HOPA.ZoomManager import ZoomManager


class SparksActionDefault(MixinGroup, SparksAction):
    def __init__(self):
        super(SparksActionDefault, self).__init__()

        self.sparksObject = None

        self.sparksPosition = None
        self.sparksSecondaryPos = None
        self.secondaryEffectObject = None

    def _onParams(self, params):
        super(SparksActionDefault, self)._onParams(params)

    def _onInitialize(self):
        super(SparksActionDefault, self)._onInitialize()

        self.sparksObject = self._getSparksObject()

    def _onAction(self):
        effectObject = self.getEffectObject()
        if effectObject is None:
            return False

        effectObject.setEnable(True)

        if self._changeEmmiterForm(effectObject) is False:
            return False

        # obj = self._getSparksObject()
        # objEntityNode = obj.getEntityNode()

        DemonSparks = DemonManager.getDemon("Sparks")
        if Mengine.hasTouchpad() is True and ZoomManager.getZoomOpenGroupName() is None:
            scene = SceneManager.getCurrentScene()
            if scene is None:
                if _DEVELOPMENT is True:
                    Trace.log("SparksAction", 0, "Can't place spark - current scene is None")
                return False
            HintEntityNode = scene.getMainLayer()
        else:
            HintEntityNode = DemonSparks.getEntityNode()
        effectEntityNode = effectObject.getEntityNode()

        if self.sparksSecondaryPos is not None:
            self.secondaryEffectObject = Utils.makeMovie2(DemonSparks.Group.name, "Sparks")

            HintEntityNode.addChild(self.secondaryEffectObject.getEntityNode())
            self.secondaryEffectObject.setPosition(self.sparksSecondaryPos)
            self.secondaryEffectObject.setPlay(True)

            if ArrowManager.getArrowAttach() is not None:  # if item attached to cursor we don't spark it
                effectObject.setEnable(False)
                return True

        HintEntityNode.addChild(effectEntityNode)

        effectObject.setPlay(True)

        return True

    def _changeEmmiterForm(self, effectObject):
        return False

    def _getSparksObject(self):
        # print "Invalid Sparks Object"
        return None

    def _getSparksPosition(self, Object):
        # print "Invalid Sparks Position", Object

        return 0, 0

    def _onEnd(self):
        effectObject = self.getEffectObject()

        if effectObject is None:
            return

        if effectObject.isActive() is False:
            return

        effectEntity = effectObject.getEntity()
        effectEntity.removeFromParent()
        effectObject.setEnable(False)

        if self.secondaryEffectObject is not None:
            self.secondaryEffectObject.removeFromParent()
            self.secondaryEffectObject.onFinalize()
            self.secondaryEffectObject.onDestroy()
            self.secondaryEffectObject = None
