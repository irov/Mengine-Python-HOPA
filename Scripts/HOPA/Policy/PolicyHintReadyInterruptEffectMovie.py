from Foundation.GroupManager import GroupManager
from Foundation.Task.TaskAlias import TaskAlias


class PolicyHintReadyInterruptEffectMovie(TaskAlias):
    def _onParams(self, params):
        super(PolicyHintReadyInterruptEffectMovie, self)._onParams(params)
        pass

    def _onGenerate(self, source):
        Effect_HintReady = GroupManager.getObject("HintEffect", "Movie_HintReady")
        if Effect_HintReady.getPlay() is False:
            return

        source.addTask("TaskMovieInterrupt", GroupName="HintEffect", MovieName="Movie_HintReady")
        source.addTask("TaskMovieStop", GroupName="HintEffect", MovieName="Movie_HintReady")
        source.addTask("TaskMovieStop", GroupName="Hint", MovieName="Movie_Ready")
        source.addTask("TaskEnable", GroupName="Hint", ObjectName="Movie_Ready", Value=False)
        pass

    pass
