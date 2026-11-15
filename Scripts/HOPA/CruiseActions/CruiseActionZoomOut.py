from HOPA.CruiseAction import CruiseAction
from HOPA.CruiseControlManager import CruiseControlManager
from HOPA.ZoomManager import ZoomManager


class CruiseActionZoomOut(CruiseAction):
    def _getCruiseObject(self):
        zoomGroupName = ZoomManager.getZoomOpenGroupName()
        if zoomGroupName is None:
            return None

        if ZoomManager.hasButtonClose(zoomGroupName) is False:
            return None

        buttonClose = ZoomManager.getButtonClose(zoomGroupName)
        return buttonClose

    def _onCheck(self):
        if ZoomManager.getZoomOpenGroupName() is None:
            return False

        return True

    def _onAction(self, source):
        click_delay = CruiseControlManager.getCruiseClickDelay('CruiseActionZoomOut')
        buttonClose = self.getCruiseObject()
        PositionTo = None
        if buttonClose is None:
            zoomGroupName = ZoomManager.getZoomOpenGroupName()
            PositionTo = ZoomManager.calcZoomPointRight(zoomGroupName)

        source.addTask("AliasCruiseControlAction", Position=PositionTo, Object=buttonClose)
        source.addDelay(click_delay)
        source.addNotify(Notificator.onCruiseActionEnd, self)
