from Foundation.Task.MixinObject import MixinObject
from HOPA.HintActions.HintActionDefault import HintActionDefault


class HintActionCollectibleItem(HintActionDefault, MixinObject):
    def _onParams(self, params):
        super(HintActionCollectibleItem, self)._onParams(params)

    def _onCheck(self):
        return True

    def _getHintObject(self):
        return self.Object

    def _getHintPosition(self, Object):
        hotspot = Object.getSocket('socket')
        position = hotspot.getWorldPolygonCenter()
        return position
