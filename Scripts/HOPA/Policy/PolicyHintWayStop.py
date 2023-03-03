from Foundation.GroupManager import GroupManager
from Foundation.Task.TaskAlias import TaskAlias


class PolicyHintWayStop(TaskAlias):
    def _onParams(self, params):
        super(PolicyHintWayStop, self)._onParams(params)
        pass

    def _onGenerate(self, source):
        Movie2_HintWay = GroupManager.getObject("HintEffect", "Movie2_HintWay")
        if Movie2_HintWay.getPlay() is False:
            return

        source.addTask("TaskMovie2Stop", GroupName="HintEffect", Movie2Name="Movie2_HintWay")
        pass

    pass
