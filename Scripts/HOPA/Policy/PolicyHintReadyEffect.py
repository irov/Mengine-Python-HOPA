from Foundation.DemonManager import DemonManager
from Foundation.Task.TaskAlias import TaskAlias


class PolicyHintReadyEffect(TaskAlias):
    def _onParams(self, params):
        super(PolicyHintReadyEffect, self)._onParams(params)
        self.Hint = DemonManager.getDemon("Hint")
        pass

    def _onGenerate(self, source):
        Position = self.Hint.getPoint()

        source.addTask("TaskObjectSetPosition", GroupName="HintEffect", ObjectName="Movie_HintReady", Value=Position)
        source.addTask("TaskEnable", GroupName="HintEffect", ObjectName="Movie_HintReady", Value=True)
        source.addTask("TaskMoviePlay", GroupName="HintEffect", MovieName="Movie_HintReady",
                       Loop=True, Wait=False, ValidationGroupEnable=False)
        pass

    pass
