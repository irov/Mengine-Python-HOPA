from Foundation.SystemManager import SystemManager
from Foundation.Task.TaskAlias import TaskAlias

class PolicyTransitionBackWay(TaskAlias):
    def _onParams(self, params):
        super(PolicyTransitionBackWay, self)._onParams(params)
        self.PositionTo = params.get("Position")
        self.effect = params.get("Effect")
        pass

    def _onGenerate(self, source):
        SystemHint = SystemManager.getSystem("SystemHint")
        self.Hint = SystemHint.getHintObject()
        Movie_HintWay = "Movie2_HintWay"

        Pfrom = self.Hint.getPoint()
        Pto = self.PositionTo
        Pbetween = (Pto[0] + abs(Pto[0] - Pfrom[0]) * 1.4, Pto[1] - abs(Pto[0] - Pfrom[0]) * 1.33)

        source.addTask("TaskMovie2Play", GroupName="HintEffect", Movie2Name=Movie_HintWay, Loop=True, Wait=False)
        source.addTask("TaskObjectSetPosition", GroupName="HintEffect", ObjectName=Movie_HintWay, Value=Pfrom)
        source.addTask("AliasObjectBezier2To", GroupName="HintEffect", ObjectName=Movie_HintWay, Point1=Pbetween, To=Pto, Time=1000.0)

        with source.addParallelTask(2) as (tc_interrupt, tc_play):
            tc_interrupt.addTask("TaskMovie2Interrupt", GroupName="HintEffect", Movie2Name=Movie_HintWay)
            # tc_interrupt.addTask("TaskMovie2Stop", GroupName="HintEffect", Movie2Name=Movie_HintWay)
            tc_play.addTask("TaskMovie2Play", Movie2=self.effect, Wait=True, Loop=True, AutoEnable=True)
        pass
    pass