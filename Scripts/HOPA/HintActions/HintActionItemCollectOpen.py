from Foundation.Task.MixinObject import MixinObject
from HOPA.HintActions.HintActionDefault import HintActionDefault


class HintActionItemCollectOpen(HintActionDefault, MixinObject):
    def _onParams(self, params):
        super(HintActionItemCollectOpen, self)._onParams(params)

    def _onCheck(self):
        return True

    def _getHintObject(self):
        return self.Object

    def _getHintPosition(self, Object):
        ObjectType = Object.getType()
        ObjectEntity = Object.getEntity()

        if ObjectType == "ObjectMovieItem":
            return self._getMovieItemHintPosition(Object)

        elif ObjectType == "ObjectItem":
            Sprite = ObjectEntity.getSprite()
            Position = Sprite.getWorldImageCenter()

        else:
            if Object.hasParam("HintPoint") is True:
                hintPoint = Object.calcWorldHintPoint()
                if hintPoint is not None:
                    return hintPoint
            hotspot = ObjectEntity.getHotSpot()
            Position = hotspot.getWorldPolygonCenter()

        return Position

    def _getMovieItemHintPosition(self, MovieItem):
        MovieItemEntity = MovieItem.getEntity()

        HintPoint = MovieItemEntity.getHintPoint()
        return HintPoint.x, HintPoint.y
