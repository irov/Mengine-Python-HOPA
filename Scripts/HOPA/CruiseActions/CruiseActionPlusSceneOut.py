from Foundation.GroupManager import GroupManager
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

    def _onAction(self, source):
        click_delay = CruiseControlManager.getCruiseClickDelay('CruiseActionPlusSceneOut')

        source.addNotify(Notificator.onItemZoomLeaveOpenZoom)
        source.addDelay(click_delay)
        source.addNotify(Notificator.onCruiseActionEnd, self)
