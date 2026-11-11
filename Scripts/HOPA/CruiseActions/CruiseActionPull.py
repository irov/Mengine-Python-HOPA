from Foundation.Task.MixinObject import MixinObject
from HOPA.CruiseAction import CruiseAction


class CruiseActionPull(CruiseAction, MixinObject):
    s_directions = {
        "Up": (0, -200),
        'UpRight': (150, -150),
        'Right': (200, 0),
        "DownRight": (150, 150),
        "Down": (0, 200),
        "DownLeft": (-150, 150),
        "Left": (-200, 0),
        "UpLeft": (-150, -150)
    }

    def _onParams(self, params):
        super(CruiseActionPull, self)._onParams(params)
        self.Direction = params.get("Direction")
        pass

    def _getCruiseObject(self):
        return self.Object
        pass

    def _getCruisePosition(self, Object):
        ObjectEntity = Object.getEntity()

        if Object.getType() == "ObjectItem":
            Sprite = ObjectEntity.getSprite()
            Position = Sprite.getWorldImageCenter()
            pass
        else:
            hintPoint = Object.calcWorldHintPoint()
            if hintPoint is not None:
                return hintPoint
            hotspot = ObjectEntity.getHotSpot()
            Position = hotspot.getWorldPolygonCenter()

        return Position

    def _onCheck(self):
        return True

    def _onAction(self, source):
        Node = Mengine.getArrowNode()
        PositionA = self._getCruisePosition(self.Object)
        PositionB = (
            PositionA[0] + CruiseActionPull.s_directions[self.Direction][0],
            PositionA[1] + CruiseActionPull.s_directions[self.Direction][1]
        )

        speed = 750

        source.addTask("TaskNodeMoveTo", Node=Node, To=PositionA, Speed=speed)
        source.addTask("TaskCursorSetPosition", Position=PositionA)
        source.addTask("TaskCursorClickEmulate", Position=PositionA, Value=True)
        source.addTask("TaskNodeMoveTo", Node=Node, To=PositionB, Speed=speed)
        source.addTask("TaskCursorSetPosition", Position=PositionB)
        source.addTask("TaskCursorClickEmulate", Position=PositionB, Value=False)

        # source.addListener(Notificator.onMousePullComplete)
        source.addListener(Notificator.onQuestEnd, Filter=self.check)
        source.addDelay(0.5 * 1000)  # speed fix
        source.addNotify(Notificator.onCruiseActionEnd, self)

    def check(self, quest):
        if quest is not self.Quest:
            return False
        return True
