from Foundation.Task.MixinObject import MixinObject
from HOPA.HintActions.HintActionDefault import HintActionDefault

class HintActionFindMana(HintActionDefault, MixinObject):
    def _onParams(self, params):
        super(HintActionFindMana, self)._onParams(params)
        pass

    def _getHintObject(self):
        return self.Object
        pass

    def _getHintPosition(self, Object):
        ObjectEntity = Object.getEntity()
        hotspot = ObjectEntity.getSocket("socket")
        Position = hotspot.getWorldPolygonCenter()
        return Position
        pass

    pass