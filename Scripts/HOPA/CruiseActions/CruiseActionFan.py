from Foundation.GroupManager import GroupManager
from HOPA.CruiseActions.CruiseActionDefault import CruiseActionDefault

class CruiseActionFan(CruiseActionDefault):
    def _onParams(self, Params):
        super(CruiseActionFan, self)._onParams(Params)

        self.ItemObjectName = Params["ItemObjectName"]
        pass

    def _getCruiseObject(self):
        Object = GroupManager.getObject(self.GroupName, self.ItemObjectName)

        return Object
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

    pass