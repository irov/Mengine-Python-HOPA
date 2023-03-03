from Foundation.DemonManager import DemonManager
from Foundation.Task.TaskAlias import TaskAlias


class PolicyHintWayTargetLoopEffect(TaskAlias):
    def _onParams(self, params):
        super(PolicyHintWayTargetLoopEffect, self)._onParams(params)
        self.Hint = DemonManager.getDemon("Hint")
        self.PositionTo = params.get("PositionTo")
        self.Point = params.get("Point", None)
        pass

    def _onGenerate(self, source):
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

        source.addTask("TaskObjectSetPosition", GroupName="HintEffect", ObjectName="Movie_HintWay", Value=P0)
        source.addTask("TaskSoundEffect", SoundName="SparklesCircle", Wait=False)
        source.addTask("TaskMoviePlay", GroupName="HintEffect", MovieName="Movie_HintWay", Loop=True, Wait=False)

        source.addTask("AliasObjectBezier2To", GroupName="HintEffect", ObjectName="Movie_HintWay",
                       Point1=P1, To=P2, Speed=600 * 0.001)  # speed fix
        pass

    pass
