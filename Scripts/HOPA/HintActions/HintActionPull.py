from Foundation.Task.MixinObject import MixinObject
from HOPA.HintActions.HintActionDefault import HintActionDefault


class HintActionPull(HintActionDefault, MixinObject):
    def _onParams(self, params):
        super(HintActionPull, self)._onParams(params)
        pass

    def _getHintObject(self):
        return self.Object
        pass

    def _getHintPosition(self, Object):
        ObjectEntity = Object.getEntity()

        if Object.getType() == "ObjectItem":
            Sprite = ObjectEntity.getSprite()
            Position = Sprite.getWorldImageCenter()
            pass
        else:
            hintPoint = Object.calcWorldHintPoint()
            if hintPoint is not None:
                return hintPoint
            hotspot = ObjectEntity.getHotSpot()
            Position = hotspot.getWorldPolygonCenter()
            pass

        return Position
        pass

    pass
