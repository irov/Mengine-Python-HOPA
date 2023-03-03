from Foundation.GroupManager import GroupManager
from Foundation.Task.TaskAlias import TaskAlias


class PolicyHintTargetStop(TaskAlias):
    def _onParams(self, params):
        super(PolicyHintTargetStop, self)._onParams(params)
        pass

    def _onGenerate(self, source):
        Movie2_HintTarget = GroupManager.getObject("HintEffect", "Movie2_HintTarget")
        if Movie2_HintTarget.getPlay() is False:
            return

        source.addTask("TaskMovie2Stop", GroupName="HintEffect", Movie2Name="Movie2_HintTarget")
        # source.addTask("TaskMovieLastFrame", GroupName="HintEffect", MovieName="Movie2_HintTarget")
        pass

    pass
