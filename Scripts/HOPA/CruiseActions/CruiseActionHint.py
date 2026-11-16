from Foundation.Notificator import Notificator
from Foundation.SystemManager import SystemManager
from HOPA.CruiseAction import CruiseAction
from HOPA.CruiseControlManager import CruiseControlManager
from HOPA.HintManager import HintManager


class CruiseActionHint(CruiseAction):
    def __init__(self):
        super(CruiseActionHint, self).__init__()
        self.Point = None
        self.click_delay = CruiseControlManager.getCruiseClickDelay('CruiseActionHint')
        self.move_delay = CruiseControlManager.getCruiseMoveDelay('CruiseActionHint')

    def _onCheck(self):
        SystemHint = SystemManager.getSystem("SystemHint")
        DemonHint = SystemHint.getHintObject()

        if not DemonHint.isActive():
            return False

        Entity = DemonHint.getEntity()

        if Entity is None:
            return False

        hintAction = Entity.hintGive()

        if hintAction is None:
            hintAction = HintManager.findGlobalHint(DemonHint)

            if hintAction is None:
                return False

        result = self.__checkHintPoint(hintAction)

        # the hint action is only a probe for the cursor point
        HintManager.finalizeHintAction(hintAction)

        return result

    def __checkHintPoint(self, hintAction):
        hintActionObj = hintAction.getHintObject()
        if hintActionObj is None:
            return False

        self.Point = hintAction.getHintPosition(hintActionObj)

        if self.Point is None:
            return False

        self.Point = self.__getItemClickPoint(hintActionObj, self.Point)
        return True

    @staticmethod
    def __getItemClickPoint(object_, point):
        object_type = object_.getType()
        if object_type not in ("ObjectMovieItem", "ObjectMovie2Item"):
            return point

        entity = object_.getEntity()
        if object_type == "ObjectMovie2Item":
            movie = entity.getCurrentEnabledMovie()
        else:
            movie = entity.getCurrentMovie()

        if movie is None:
            return point

        if movie.hasSocket("socket") is False:
            return point

        socket = movie.getSocket("socket")
        candidates = [point]
        for vertex in socket.getWorldPolygon().getPoints():
            candidate = Mengine.vec2f(point[0] + (vertex[0] - point[0]) * 0.75, point[1] + (vertex[1] - point[1]) * 0.75)
            candidates.append(candidate)

        for candidate in candidates:
            screen = Mengine.fromWorldToScreenPosition((candidate[0], candidate[1], 0.0))
            pickers = Mengine.pickAllHotspot(screen)
            if len(pickers) == 0:
                continue

            if pickers[-1] == socket:
                return candidate

        return point

    def _onAction(self, source):
        Obj = self.Quest.params.get("Object", None) if self.Quest else None

        source.addDelay(self.click_delay)
        source.addTask("AliasCruiseControlAction", Position=self.Point, Object=Obj)
        source.addDelay(self.move_delay)
        source.addNotify(Notificator.onCruiseActionEnd, self)
