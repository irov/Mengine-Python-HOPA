from Foundation.Task.MixinObject import MixinObject
from Foundation.TaskManager import TaskManager
from HOPA.HintActions.HintActionMultiTarget import HintActionMultiTarget
from HOPA.ElementalMagicManager import ElementalMagicManager


class HintActionElementalMagicUse(MixinObject, HintActionMultiTarget):

    def _onParams(self, params):
        super(HintActionElementalMagicUse, self)._onParams(params)

        self.Ring = ElementalMagicManager.getMagicRing()
        self.Element = params["Element"]

    def _getHintObject(self):
        return self.Object

    def _onCheck(self):
        if ElementalMagicManager.getPlayerElement() == self.Element:
            return True
        return False

    def _onAction(self, hint):
        PositionTo1, PositionTo2 = self.getMultiHintPosition()
        self.showHint(PositionTo1, PositionTo2)

    def getMultiHintPosition(self):
        node = self.Ring.getRootNode()
        PositionTo1 = node.getWorldPosition()

        ObjectEntity = self.Object.getEntity()
        Sprite = ObjectEntity.getSprite()
        PositionTo2 = Sprite.getWorldImageCenter()

        return PositionTo1, PositionTo2
