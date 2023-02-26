from Foundation.DemonManager import DemonManager
from Foundation.GroupManager import GroupManager
from HOPA.Entities.BoneBoard.BoneBoardManager import BoneBoardManager
from HOPA.HintActions.HintActionDefault import HintActionDefault

class HintActionBoneUse(HintActionDefault):
    def __init__(self):
        super(HintActionBoneUse, self).__init__()
        pass

    def _onParams(self, params):
        super(HintActionBoneUse, self)._onParams(params)
        self.bone_key = params.get("BoneKey")
        pass

    def _getHintObject(self):
        ItemName = BoneBoardManager.getItemName(self.bone_key)
        BoneObject = GroupManager.getObject("BonePlates", ItemName)
        return BoneObject
        pass

    def _getHintPosition(self, Object):
        ObjectEntity = Object.getEntity()
        Sprite = ObjectEntity.getSprite()
        Position = Sprite.getWorldImageCenter()
        return Position
        pass

    def _onAction(self, hint):
        super(HintActionBoneUse, self)._onAction(hint)
        BoneBoardObject = DemonManager.getDemon("BoneBoard")
        BoneBoardEntity = BoneBoardObject.getEntity()
        BoneBoardEntity.showBoard()
        pass