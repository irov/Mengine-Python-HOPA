from Foundation.GroupManager import GroupManager
from Foundation.Task.TaskAlias import TaskAlias

class PolicyHintWayEffectInterrupt(TaskAlias):
    def _onParams(self, params):
        super(PolicyHintWayEffectInterrupt, self)._onParams(params)
        pass

    def _onGenerate(self, source):
        Movie_HintWay = GroupManager.getObject("HintEffect", "Movie2_HintWay")
        if Movie_HintWay.getPlay() is False:
            return
            pass
        source.addTask("TaskMovie2Interrupt", GroupName="HintEffect", Movie2Name="Movie2_HintWay")
        # source.addTask("TaskMovie2Stop", GroupName = "HintEffect", Movie2Name = "Movie2_HintWay")
        pass
    pass