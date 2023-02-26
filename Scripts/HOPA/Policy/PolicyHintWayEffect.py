from Foundation.SystemManager import SystemManager
from Foundation.Task.TaskAlias import TaskAlias

class PolicyHintWayEffect(TaskAlias):
    def _onParams(self, params):
        super(PolicyHintWayEffect, self)._onParams(params)
        self.PositionTo = params.get("Position")
        self.Point = params.get("Point", None)
        self.NodeTo = params.get("NodeTo", None)
        pass

    def _onGenerate(self, source):
        if self.NodeTo is None:
            SystemHint = SystemManager.getSystem("SystemHint")
            self.Hint = SystemHint.getHintObject()

            if self.Point is None:
                P0 = self.Hint.getPoint()
                pass
            else:
                P0 = self.Point
                pass

            P2 = self.PositionTo

            p1x = P0[0] if P0[1] > P2[1] else P2[0]
            p1y = P2[1] if P0[1] > P2[1] else P0[1]

            P1 = (p1x, p1y)
            name = "Movie2_HintWay"

            source.addTask("TaskObjectSetPosition", GroupName="HintEffect", ObjectName=name, Value=P0)
            source.addTask("TaskMovie2Play", GroupName="HintEffect", Movie2Name=name, Loop=True, Wait=False)

            source.addTask("AliasObjectBezier2To", GroupName="HintEffect", ObjectName=name, Point1=P1, To=P2, Speed=600 * 0.001)  # speed fix
        else:
            SystemHint = SystemManager.getSystem("SystemHint")
            self.Hint = SystemHint.getHintObject()

            if self.Point is None:
                P0 = self.Hint.getPoint()
                pass
            else:
                P0 = self.Point
                pass

            P2 = self.PositionTo

            p1x = P0[0] if P0[1] > P2[1] else P2[0]
            p1y = P2[1] if P0[1] > P2[1] else P0[1]

            P1 = (p1x, p1y)
            name = "Movie2_HintWay"

            source.addTask("TaskObjectSetPosition", GroupName="HintEffect", ObjectName=name, Value=P0)
            source.addTask("TaskMovie2Play", GroupName="HintEffect", Movie2Name=name, Loop=True, Wait=False)

            source.addTask("AliasObjectBezier2Follow", GroupName="HintEffect", ObjectName=name, Follow=self.NodeTo, Time=1000.0)  # speed fix
            pass
        pass
    pass