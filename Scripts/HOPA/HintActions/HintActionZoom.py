from Foundation.Task.MixinObjectTemplate import MixinZoom
from HOPA.HintActions.HintActionDefault import HintActionDefault
from HOPA.ZoomManager import ZoomManager


class HintActionZoom(MixinZoom, HintActionDefault):
    def _onParams(self, params):
        super(HintActionZoom, self)._onParams(params)
        pass

    def _getHintObject(self):
        return self.Zoom
        pass

    def _onCheck(self):
        ZoomGroupName = ZoomManager.getZoomGroupName(self.Zoom)

        ZoomDesc = ZoomManager.getZoom(ZoomGroupName)

        Open = ZoomDesc.getOpen()

        if Open is True:
            return False
            pass

        BlockOpen = self.Zoom.getParam("BlockOpen")
        if BlockOpen is True:
            return False
            pass

        return True
        pass

    def _getHintPosition(self, Object):
        hintPoint = Object.getHintPoint()
        if hintPoint is not None:
            return hintPoint

        ObjectEntity = Object.getEntity()

        HotSpot = ObjectEntity.getHotSpot()
        Position = HotSpot.getWorldPolygonCenter()

        return Position
