from Foundation.DemonManager import DemonManager
from HOPA.HintActions.HintActionUseInventoryItem import HintActionUseInventoryItem

class HintActionBoneAdd(HintActionUseInventoryItem):
    def __init__(self):
        super(HintActionBoneAdd, self).__init__()
        pass

    def _onParams(self, params):
        super(HintActionBoneAdd, self)._onParams(params)
        pass

    def _onAction(self, hint):
        super(HintActionBoneAdd, self)._onAction(hint)
        BoneBoardObject = DemonManager.getDemon("BoneBoard")
        BoneBoardEntity = BoneBoardObject.getEntity()
        BoneBoardEntity.showBoard()
        pass