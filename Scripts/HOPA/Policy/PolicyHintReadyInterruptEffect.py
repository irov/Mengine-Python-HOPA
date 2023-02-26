from Foundation.GroupManager import GroupManager
from Foundation.Task.TaskAlias import TaskAlias

class PolicyHintReadyInterruptEffect(TaskAlias):
    def _onParams(self, params):
        super(PolicyHintReadyInterruptEffect, self)._onParams(params)
        pass

    def _onGenerate(self, source):
        Effect_HintReady = GroupManager.getObject("HintEffect", "Movie_HintReady")
        if Effect_HintReady.getPlay() is False:
            return

        # source.addTask("TaskEffectInterrupt", GroupName = "HintEffect", EffectName = "Movie_HintReady")
        source.addTask("TaskMovieStop", GroupName="HintEffect", MovieName="Movie_HintReady")
        pass
    pass