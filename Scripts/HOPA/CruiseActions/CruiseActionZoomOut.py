from HOPA.CruiseAction import CruiseAction
from HOPA.CruiseControlManager import CruiseControlManager
from HOPA.ZoomManager import ZoomManager


class CruiseActionZoomOut(CruiseAction):
    def _getCruiseObject(self):
        zoomGroupName = ZoomManager.getZoomOpenGroupName()
        buttonClose = ZoomManager.getButtonClose(zoomGroupName)
        return buttonClose

    def _getCruisePosition(self):
        zoomGroupName = ZoomManager.getZoomOpenGroupName()

        if ZoomManager.hasButtonClose(zoomGroupName) is False:
            Position = ZoomManager.calcZoomPointRight(zoomGroupName)
            return Position

        buttonClose = ZoomManager.getButtonClose(zoomGroupName)
        buttonCloseEntity = buttonClose.getEntity()

        Position = buttonCloseEntity.getSprite().getWorldImageCenter()

        return Position

    def _onAction(self, source):
        click_delay = CruiseControlManager.getCruiseClickDelay('CruiseActionZoomOut')
        PositionTo = self._getCruisePosition()

        source.addTask("AliasCruiseControlAction", Position=PositionTo, Object=self._getCruiseObject())
        source.addDelay(click_delay)
        source.addNotify(Notificator.onCruiseActionEnd, self)
