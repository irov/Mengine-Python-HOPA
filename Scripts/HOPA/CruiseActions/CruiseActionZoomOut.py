from Foundation.TaskManager import TaskManager
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

    def onAction(self):
        click_delay = CruiseControlManager.getCruiseClickDelay('CruiseActionZoomOut')
        PositionTo = self._getCruisePosition()
        if TaskManager.existTaskChain("CruiseActionZoomOut") is True:
            TaskManager.cancelTaskChain("CruiseActionZoomOut")

        with TaskManager.createTaskChain(Name="CruiseActionZoomOut") as tc:
            tc.addTask("AliasCruiseControlAction", Position=PositionTo, Object=self._getCruiseObject())
            tc.addDelay(click_delay)
            tc.addTask("TaskNotify", ID=Notificator.onCruiseActionEnd, Args=(self,))