from Foundation.GroupManager import GroupManager
from Foundation.Task.TaskAlias import TaskAlias

class PolicyHintTargetInventoryStop(TaskAlias):
    def _onParams(self, params):
        super(PolicyHintTargetInventoryStop, self)._onParams(params)
        pass

    def _onGenerate(self, source):
        Movie2_HintInventoryTarget = GroupManager.getObject("HintEffect", "Movie2_HintInventoryTarget")
        if Movie2_HintInventoryTarget.getPlay() is False:
            return

        source.addTask("TaskMovie2Stop", GroupName="HintEffect", Movie2Name="Movie2_HintInventoryTarget")
        pass
    pass