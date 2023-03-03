from Foundation.GroupManager import GroupManager
from Foundation.Task.TaskAlias import TaskAlias


class PolicyHintTargetLoopInterruptEffect(TaskAlias):
    def _onParams(self, params):
        super(PolicyHintTargetLoopInterruptEffect, self)._onParams(params)
        pass

    def _onGenerate(self, source):
        Effect_HintTargetLoop = GroupManager.getObject("HintEffect", "Movie_HintTargetLoop")
        if Effect_HintTargetLoop.getPlay() is False:
            return
        Effect_HintTargetLoop.setLoop(False)
        source.addTask("TaskMovieInterrupt", GroupName="HintEffect", MovieName="Movie_HintTargetLoop")
        source.addTask("TaskMovieStop", GroupName="HintEffect", MovieName="Movie_HintTargetLoop")
        pass

    pass
