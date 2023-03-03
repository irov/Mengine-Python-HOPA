from Foundation.DemonManager import DemonManager
from HOPA.CruiseActions.CruiseActionUseInventoryItem import CruiseActionUseInventoryItem


class CruiseActionBoneAdd(CruiseActionUseInventoryItem):
    def __init__(self):
        super(CruiseActionBoneAdd, self).__init__()
        pass

    def _onParams(self, params):
        super(CruiseActionBoneAdd, self)._onParams(params)
        pass

    def _onAction(self, Cruise):
        super(CruiseActionBoneAdd, self)._onAction(Cruise)
        BoneBoardObject = DemonManager.getDemon("BoneBoard")
        BoneBoardEntity = BoneBoardObject.getEntity()
        BoneBoardEntity.showBoard()
        pass
