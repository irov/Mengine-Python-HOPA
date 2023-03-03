from HOPA.HintActions.HintActionDefault import HintActionDefault

from HOPA.ZoomManager import ZoomManager


class HintActionZoomOut(HintActionDefault):
    def _getHintObject(self):
        return None
        pass

    def _getHintPosition(self, Object):
        zoomGroupName = ZoomManager.getZoomOpenGroupName()

        if ZoomManager.hasButtonClose(zoomGroupName) is False:
            Position = ZoomManager.calcZoomPointRight(zoomGroupName)
            return Position

        buttonClose = ZoomManager.getButtonClose(zoomGroupName)
        buttonCloseEntity = buttonClose.getEntity()

        Position = buttonCloseEntity.getSprite().getWorldImageCenter()

        return Position
