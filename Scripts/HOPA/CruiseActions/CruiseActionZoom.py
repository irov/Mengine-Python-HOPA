from Foundation.Task.MixinObjectTemplate import MixinZoom
from HOPA.CruiseAction import CruiseAction
from HOPA.CruiseControlManager import CruiseControlManager
from HOPA.ZoomManager import ZoomManager


class CruiseActionZoom(MixinZoom, CruiseAction):
    def _onParams(self, params):
        super(CruiseActionZoom, self)._onParams(params)
        self.click_delay = CruiseControlManager.getCruiseClickDelay('CruiseActionZoom')

    def _getCruiseObject(self):
        return self.Zoom

    def _onCheck(self):
        ZoomGroupName = ZoomManager.getZoomGroupName(self.Zoom)

        ZoomDesc = ZoomManager.getZoom(ZoomGroupName)

        Open = ZoomDesc.getOpen()

        if Open is True:
            return False

        BlockOpen = self.Zoom.getParam("BlockOpen")
        if BlockOpen is True:
            return False

        return True

    def _getCruisePosition(self, Object):
        cruisePoint = Object.getHintPoint()
        if cruisePoint is not None:
            return cruisePoint

        ObjectEntity = Object.getEntity()

        HotSpot = ObjectEntity.getHotSpot()
        Position = HotSpot.getWorldPolygonCenter()

        return Position

    def _onAction(self, source):
        PositionTo = self._getCruisePosition(self.Zoom)

        source.addTask("AliasCruiseControlAction", Position=PositionTo, Object=self.Zoom)
        source.addDelay(self.click_delay)
        source.addNotify(Notificator.onCruiseActionEnd, self)
