from Foundation.SystemManager import SystemManager
from Foundation.Task.TaskAlias import TaskAlias


class PolicyHintActivateWayEffect(TaskAlias):
    def _onParams(self, params):
        super(PolicyHintActivateWayEffect, self)._onParams(params)
        self.PositionTo = params.get("Position")
        self.Point = params.get("Point", None)
        pass

    def _onGenerate(self, source):
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

        MovieGroup = self.Hint.getGroup()
        Movie_Activate = MovieGroup.getObject("Movie2_Activate")
        Movie_Reload = MovieGroup.getObject("Movie2_Reload")
        Movie_HintWay = "Movie2_HintWay"

        source.addDisable(Movie_Reload)
        source.addEnable(Movie_Activate)
        source.addTask("TaskMoviePlay", Movie=Movie_Activate)
        source.addDisable(Movie_Activate)

        source.addTask("TaskObjectSetPosition", GroupName="HintEffect", ObjectName=Movie_HintWay, Value=P0)
        source.addTask("TaskMovie2Play", GroupName="HintEffect", Movie2Name=Movie_HintWay, Loop=True, Wait=False)

        source.addTask("AliasObjectBezier2To", GroupName="HintEffect", ObjectName=Movie_HintWay,
                       Point1=P1, To=P2, Speed=600 * 0.001)  # speed fix
        pass

    pass
