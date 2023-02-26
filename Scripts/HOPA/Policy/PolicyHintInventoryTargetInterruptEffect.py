from Foundation.GroupManager import GroupManager
from Foundation.Task.TaskAlias import TaskAlias

class PolicyHintInventoryTargetInterruptEffect(TaskAlias):
    def _onParams(self, params):
        super(PolicyHintInventoryTargetInterruptEffect, self)._onParams(params)
        pass

    def _onGenerate(self, source):
        Effect_HintInventoryTarget = GroupManager.getObject("HintEffect", "Movie2_HintInventoryTarget")
        if Effect_HintInventoryTarget.getPlay() is False:
            return

        source.addTask("TaskMovie2Interrupt", GroupName="HintEffect", Movie2Name="Movie2_HintInventoryTarget")  # NoSkipStop=True
        pass
    pass