from Foundation.DefaultManager import DefaultManager
from Foundation.Notificator import Notificator
from HOPA.CruiseActions.CruiseActionClick import CruiseActionClick


class CruiseActionEnter(CruiseActionClick):
    def _onCheck(self):
        if self.Object.isActive() is False:
            return False

        return True

    def _getCruisePosition(self, object_):
        object_type = object_.getType()
        if object_type in ("ObjectSocket", "ObjectButton", "ObjectTransition"):
            position = object_.calcWorldHintPoint()
            return position

        if object_type == "ObjectMovieButton":
            position = object_.getCurrentMovieSocketCenter()
            return position

        position = super(CruiseActionEnter, self)._getCruisePosition(object_)
        return position

    def _onAction(self, source):
        position = self._getCruisePosition(self.Object)
        arrow = Mengine.getArrowNode()
        speed = DefaultManager.getDefaultFloat("CruiseControlCursorSpeed", 700.0)

        source.addTask("TaskNodeMoveTo", Node=arrow, To=position, Speed=speed, Easing="easyCubicOut")
        source.addTask("TaskCursorSetPosition", Position=position)
        source.addNextFrame()  # allow the real mouse-enter event to complete the quest
        source.addNotify(Notificator.onCruiseActionEnd, self)
        pass
