from Foundation.DemonManager import DemonManager
from Foundation.GroupManager import GroupManager
from Foundation.Task.TaskAlias import TaskAlias


class PolicyHintReadyEffectMovie(TaskAlias):
    def _onParams(self, params):
        super(PolicyHintReadyEffectMovie, self)._onParams(params)
        self.Hint = DemonManager.getDemon("Hint")
        pass

    def _onGenerate(self, source):
        Position = self.Hint.getPoint()
        Movie_Ready = GroupManager.getObject("Hint", "Movie_Ready")
        Movie_Ready.setEnable(True)

        source.addTask("TaskObjectSetPosition", GroupName="HintEffect", ObjectName="Movie_HintReady", Value=Position)
        source.addTask("TaskMoviePlay", GroupName="HintEffect", MovieName="Movie_HintReady", Loop=True, Wait=False)
        source.addTask("TaskMoviePlay", GroupName="Hint", MovieName="Movie_Ready", Wait=False)
        pass

    pass
