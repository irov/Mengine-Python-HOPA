from Foundation.GroupManager import GroupManager
from Foundation.TaskManager import TaskManager
from HOPA.CruiseAction import CruiseAction
from HOPA.CruiseControlManager import CruiseControlManager

class CruiseActionPlusSceneOut(CruiseAction):
    def _getCruisePosition(self):
        group = GroupManager.getGroup("ItemPlusDefault")
        buttonMovieClose = group.getObject("MovieButton_Close")
        buttonMovieCloseEntity = buttonMovieClose.getEntity()

        movieEntity = buttonMovieCloseEntity.getCurrentMovie().getEntity()
        socket = movieEntity.getSocket("socket")

        Position = socket.getWorldPolygonCenter()

        return Position

    def onCheck(self):
        return True

    def onAction(self):
        click_delay = CruiseControlManager.getCruiseClickDelay('CruiseActionPlusSceneOut')
        if TaskManager.existTaskChain("CruiseActionPlusSceneOut") is True:
            TaskManager.cancelTaskChain("CruiseActionPlusSceneOut")

        with TaskManager.createTaskChain(Name="CruiseActionPlusSceneOut") as tc:
            tc.addTask("TaskNotify", ID=Notificator.onItemZoomLeaveOpenZoom)
            tc.addDelay(click_delay)
            tc.addTask("TaskNotify", ID=Notificator.onCruiseActionEnd, Args=(self,))