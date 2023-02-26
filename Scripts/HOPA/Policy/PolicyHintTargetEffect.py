from Foundation.Task.TaskAlias import TaskAlias

class PolicyHintTargetEffect(TaskAlias):
    def _onParams(self, params):
        super(PolicyHintTargetEffect, self)._onParams(params)
        self.Position = params.get("Position")
        pass

    def _onGenerate(self, source):
        source.addTask("TaskObjectSetPosition", GroupName="HintEffect", ObjectName="Movie_HintTarget", Value=self.Position)
        source.addTask("TaskMoviePlay", GroupName="HintEffect", MovieName="Movie_HintTarget", Wait=True)
        pass

    pass