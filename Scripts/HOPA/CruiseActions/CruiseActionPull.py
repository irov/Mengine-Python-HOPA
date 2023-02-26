from Foundation.Task.MixinObject import MixinObject
from Foundation.TaskManager import TaskManager
from HOPA.CruiseAction import CruiseAction

class CruiseActionPull(CruiseAction, MixinObject):
    s_directions = {"Up": (0, -200), 'UpRight': (150, -150), 'Right': (200, 0), "DownRight": (150, 150), "Down": (0, 200), "DownLeft": (-150, 150), "Left": (-200, 0), "UpLeft": (-150, -150)}
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
            pass

        return Position
        pass

    def _onCheck(self):
        return True
        pass

    def _onAction(self):
        Node = Mengine.getArrow()
        PositionA = self._getCruisePosition(self.Object)
        PositionB = (PositionA[0] + CruiseActionPull.s_directions[self.Direction][0], PositionA[1] + CruiseActionPull.s_directions[self.Direction][1])

        if TaskManager.existTaskChain("CruiseActionPull") is True:
            TaskManager.cancelTaskChain("CruiseActionPull")
            pass

        speed = 750

        with TaskManager.createTaskChain(Name="CruiseActionPull") as tc:
            tc.addTask("TaskNodeMoveTo", Node=Node, To=PositionA, Speed=speed)
            tc.addTask("TaskCursorSetPosition", Position=PositionA)
            tc.addTask("TaskCursorClickEmulate", Position=PositionA, Value=True)
            tc.addTask("TaskNodeMoveTo", Node=Node, To=PositionB, Speed=speed)
            tc.addTask("TaskCursorSetPosition", Position=PositionB)
            tc.addTask("TaskCursorClickEmulate", Position=PositionB, Value=False)

            # tc.addTask("TaskListener", ID = Notificator.onMousePullComplete)
            tc.addTask("TaskListener", ID=Notificator.onQuestEnd, Filter=self.check)
            tc.addTask("TaskDelay", Time=0.5 * 1000)  # speed fix
            tc.addTask("TaskNotify", ID=Notificator.onCruiseActionEnd, Args=(self,))
            pass
        pass

    def check(self, quest):
        if quest is not self.Quest:
            return False
            pass
        return True
        pass

    def _onEnd(self):
        super(CruiseActionPull, self)._onEnd()

        pass
    pass