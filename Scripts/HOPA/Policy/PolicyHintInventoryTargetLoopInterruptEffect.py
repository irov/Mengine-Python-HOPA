from Foundation.GroupManager import GroupManager
from Foundation.Task.TaskAlias import TaskAlias


class PolicyHintInventoryTargetLoopInterruptEffect(TaskAlias):
    def _onParams(self, params):
        super(PolicyHintInventoryTargetLoopInterruptEffect, self)._onParams(params)
        pass

    def _onGenerate(self, source):
        Effect_HintInventoryTargetLoop = GroupManager.getObject("HintEffect", "Movie2_HintInventoryTargetLoop")
        if Effect_HintInventoryTargetLoop.getPlay() is False:
            return
        Effect_HintInventoryTargetLoop.setLoop(False)
        source.addTask("TaskMovie2Interrupt", GroupName="HintEffect", Movie2Name="Movie2_HintInventoryTargetLoop")
        # source.addTask("TaskMovie2Stop", GroupName = "HintEffect", Movie2Name = "Movie2_HintInventoryTargetLoop")
        # source.addTask("TaskMovie2Rewind", GroupName="HintEffect", Movie2Name="Movie2_HintTarget")
        pass

    pass
