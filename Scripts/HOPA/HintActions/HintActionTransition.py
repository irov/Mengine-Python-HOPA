from Foundation.Task.MixinObjectTemplate import MixinTransition
from HOPA.EnigmaManager import EnigmaManager
from HOPA.HintActions.HintActionDefault import HintActionDefault


class HintActionTransition(MixinTransition, HintActionDefault):
    def _getHintObject(self):
        return self.Transition

    def _getHintPosition(self, Object):
        hintPoint = Object.calcWorldHintPoint()
        if hintPoint is not None:
            return hintPoint

        ObjectEntity = Object.getEntity()

        HotSpot = ObjectEntity.getHotSpot()
        Position = HotSpot.getWorldPolygonCenter()

        return Position

    def _onCheck(self):
        BlockOpen = self.Transition.getParam("BlockOpen")

        if BlockOpen is True:
            return False

        if EnigmaManager.getSceneActiveEnigma() is not None:
            return False

        return True
