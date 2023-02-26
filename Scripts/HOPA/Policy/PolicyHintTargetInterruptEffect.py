from Foundation.GroupManager import GroupManager
from Foundation.Task.TaskAlias import TaskAlias

class PolicyHintTargetInterruptEffect(TaskAlias):
    def _onParams(self, params):
        super(PolicyHintTargetInterruptEffect, self)._onParams(params)
        pass

    def _onGenerate(self, source):
        Movie2_HintTarget = GroupManager.getObject("HintEffect", "Movie2_HintTarget")
        if Movie2_HintTarget.getPlay() is False:
            return

        source.addTask("TaskMovie2Interrupt", GroupName="HintEffect", Movie2Name="Movie2_HintTarget", NoSkipStop=True)

        pass
    pass