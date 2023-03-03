from Foundation.DemonManager import DemonManager
from Foundation.GroupManager import GroupManager
from HOPA.CruiseActions.CruiseActionDefault import CruiseActionDefault
from HOPA.Entities.BoneBoard.BoneBoardManager import BoneBoardManager


class CruiseActionBoneUse(CruiseActionDefault):
    def __init__(self):
        super(CruiseActionBoneUse, self).__init__()
        pass

    def _onParams(self, params):
        super(CruiseActionBoneUse, self)._onParams(params)
        self.bone_key = params.get("BoneKey")
        pass

    def _getCruiseObject(self):
        ItemName = BoneBoardManager.getItemName(self.bone_key)
        BoneObject = GroupManager.getObject("BonePlates", ItemName)
        return BoneObject
        pass

    def _getCruisePosition(self, Object):
        ObjectEntity = Object.getEntity()
        Sprite = ObjectEntity.getSprite()
        Position = Sprite.getWorldImageCenter()
        return Position
        pass

    def _onCheck(self):
        return True
        pass

    def _onAction(self, Cruise):
        super(CruiseActionBoneUse, self)._onAction(Cruise)
        BoneBoardObject = DemonManager.getDemon("BoneBoard")
        BoneBoardEntity = BoneBoardObject.getEntity()
        BoneBoardEntity.showBoard()

        pass
