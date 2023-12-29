from Foundation.Task.MixinObject import MixinObject
from Foundation.TaskManager import TaskManager
from HOPA.HintActions.HintActionMultiTarget import HintActionMultiTarget
from HOPA.ElementalMagicManager import ElementalMagicManager


class HintActionElementalMagicPick(MixinObject, HintActionMultiTarget):

    def _onParams(self, params):
        super(HintActionElementalMagicPick, self)._onParams(params)

        self.Ring = ElementalMagicManager.getMagicRing()
        self.Element = params["Element"]
        self.MagicId = params["MagicId"]

    def _getHintObject(self):
        return self.Object

    def _onCheck(self):
        if ElementalMagicManager.hasUseQuestOnElement(self.MagicId) is False:
            return False
        if ElementalMagicManager.getPlayerElement() is not None:
            return False

        # user should have use quest and be empty
        return True

    def _onAction(self, hint):
        PositionTo1, PositionTo2 = self.getMultiHintPosition()
        self.showHint(PositionTo1, PositionTo2)

    def getMultiHintPosition(self):
        node = self.Ring.getRootNode()
        PositionTo1 = node.getWorldPosition()

        ObjectEntity = self.Object.getEntity()
        HotSpot = ObjectEntity.getHotSpot()
        PositionTo2 = HotSpot.getWorldPolygonCenter()

        return PositionTo1, PositionTo2
