from Foundation.DemonManager import DemonManager
from Foundation.SystemManager import SystemManager
from Foundation.Task.MixinObjectTemplate import MixinZoom
from HOPA.HintManager import HintManager
from HOPA.SparksActions.SparksActionDefault import SparksActionDefault


class SparksActionHint(SparksActionDefault, MixinZoom):
    def __init__(self):
        super(SparksActionHint, self).__init__()

    def _onParams(self, params):
        super(SparksActionHint, self)._onParams(params)

    def _onCheck(self):
        return True

    def _getSparksObject(self):
        return self.Zoom

    def _changeEmmiterForm(self, effectObject):
        SystemHint = SystemManager.getSystem("SystemHint")
        DemonHint = SystemHint.getHintObject()
        Entity = DemonHint.getEntity()
        hintAction = Entity.hintGive()

        if hintAction is None:
            hintAction = HintManager.findGlobalHint(DemonHint)
            if hintAction is None:
                if hintAction is None:
                    return False

        hintActionObj = hintAction.getHintObject()
        if hintActionObj is None:
            return False

        if not hintAction.onCheck():
            return False

        Point = hintAction.getHintPosition(hintActionObj)

        if Point is None:
            Point = hintAction.getHintDoublePosition(hintActionObj)

            if Point is not None:
                self.sparksPosition = Point[0]
                self.sparksSecondaryPos = Point[1]

                SparksDemon = DemonManager.getDemon("Sparks")
                SparksDemon.setParam("State", "Idle")
                effectObject.setPosition(Point[0])

                return True

        if Point is None:
            return False

        SparksDemon = DemonManager.getDemon("Sparks")
        SparksDemon.setParam("State", "Idle")

        effectObject.setPosition(Point)
        return True
