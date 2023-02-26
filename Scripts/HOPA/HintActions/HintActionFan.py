from Foundation.GroupManager import GroupManager
from HOPA.HintActions.HintActionDefault import HintActionDefault

class HintActionFan(HintActionDefault):
    def _onParams(self, Params):
        super(HintActionFan, self)._onParams(Params)

        self.ItemObjectName = Params["ItemObjectName"]
        pass

    def _getHintObject(self):
        Object = GroupManager.getObject(self.GroupName, self.ItemObjectName)

        return Object
        pass

    def _getHintPosition(self, Object):
        ObjectEntity = Object.getEntity()

        Sprite = ObjectEntity.getSprite()
        Position = Sprite.getWorldImageCenter()
        return Position
        pass

    pass